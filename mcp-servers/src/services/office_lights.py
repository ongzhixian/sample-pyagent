class OfficeLightsService:

    def __init__(self):
        self.office_lights = {
            "reception": "on",
            "conference room 1": "off",
            "conference room 2": "off",
            "office": "off",
        }

    def get_office_lights(self):
        # Logic to retrieve current office lighting status
        print("Retrieving current office lights status")
        return self.office_lights
    
    def get_office_light(self, location: str):
        # Logic to retrieve the light status for a specific location
        status = self.office_lights.get(location, "unknown location")
        print(f"Retrieving light status for {location}: {status}")
        return {location: status}
    

    def toggle_office_lights(self, location: str):
        # Logic to toggle the lights in the specified location
        if location in self.office_lights:
            current_status = self.office_lights[location]
            new_status = "off" if current_status == "on" else "on"
            self.office_lights[location] = new_status
            print(f"Toggled lights in {location} to {new_status}")
            return {location: new_status}
        else:
            print(f"Location '{location}' not found")
            return {"error": "Location not found"}
        

if __name__ == "__main__":
    service = OfficeLightsService()
    print(service.get_office_lights())
    print(service.get_office_light("reception"))
    print(service.toggle_office_lights("conference room 1"))
    print(service.get_office_lights())