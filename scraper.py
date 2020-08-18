import bs4

import pymongo
import urllib.request

import constants

SERVICE_UPDATES_URL = "https://translink.com.au/service-updates"
TRANSLINK_URL = "https://translink.com.au/"

class ServiceUpdateListener:
    pass

class ServiceUpdateScraper:
    pass

def scrape_service_updates(service_updates_page: bs4.BeautifulSoup):
    service_updates_table = service_updates_page.find("table", attrs={"id":"service-notices-list"})

    unparsed_service_updates = []
    if (service_updates_table != None):
        unparsed_service_updates = service_updates_table.findAll("tr")[1:]

    service_updates = []
    for unparsed_service_update in unparsed_service_updates:
        service_update = {
            "id": "",
            "severity": "",
            "title": "",
            "dates": "",
            "url": ""
        }
        
        service_update["severity"] = unparsed_service_update.find("span", attrs={"class":"sr-only"}).text
        service_update["title"] = unparsed_service_update.find("a", attrs={"class":"show-notice-details"}).text
        service_update["url"] = TRANSLINK_URL + unparsed_service_update.find("a", attrs={"class":"show-notice-details"})["href"]
        service_update["id"] = service_update["url"].split("/")[-1]
        service_update["dates"] = unparsed_service_update.find("td", attrs={"class":"notice-date-cell gridcell hidden-xs"}).text
        service_updates.append(service_update)

    return service_updates

def scrape_affected_services(affected_services_div: bs4.BeautifulSoup):
    parsed_services = []
    for service in affected_services_div.find_all("a"):
        parsed_service = {
            "name": service.text,
            "url": service["href"]
        }
        parsed_services.append(parsed_service)

    return parsed_services

def scrape_service_update_details(service_update_page: bs4.BeautifulSoup):
    details = {
        "long_description": "",
        "affected_services": ""
    }

    details["affected_services"] = scrape_affected_services(
            service_update_page.find("div", attrs={"id":"affected-services"}))
    print("Scraped Details: " + str(details))
    return details

def add_updates_to_db(service_updates: list):
    connection = pymongo.MongoClient(constants.MONGODB_CONNECTION_URL)
    updates_db = connection.translink.service_updates
    
    stored_ids = updates_db.distinct("id")
    retrieved_ids = [service_update["id"] for service_update in service_updates]
    resolved_ids = list(set(stored_ids) - set(retrieved_ids))
    
    for resolved_id in resolved_ids:
        updates_db.delete_one({"id": resolved_id})
        print("Removed: " + str(resolved_id))

    updated_ids = []
    new_ids = []

    for update in service_updates:
        existing_service_update = updates_db.find_one({"id": update["id"]})
        if existing_service_update != None:
            existing_service_update.pop("_id")
            if existing_service_update != update:
                updated_ids.append(update["id"])
                updates_db.replace_one({"id": update["id"]}, update)
                print("Updated: " + str(update))
            else:
                continue
        else:
            new_ids.append(update["id"])
            updates_db.insert_one(update)
            print("Added: " + str(update))
        
    print("Added all to db")
    return {"resolved": resolved_ids, "new": new_ids, "updated": updated_ids}
    

def main():
    service_updates_page = bs4.BeautifulSoup(urllib.request.urlopen(SERVICE_UPDATES_URL).read())
    service_updates = scrape_service_updates(service_updates_page)
    
    print("Scraped Updates: " + str(service_updates))

    for service_update in service_updates:
        update_page = bs4.BeautifulSoup(urllib.request.urlopen(service_update["url"]).read())
        details = scrape_service_update_details(update_page)
        service_update.update(details)

    print("Finished Scraping")
    return add_updates_to_db(service_updates)

if __name__ == "__main__":
    main()