from django.core.management.base import BaseCommand
from api.models import Service, Category


class Command(BaseCommand):
    help = "Create default service categories and services"

    def handle(self, *args, **kwargs):

        services_data = [
            {
                "category": "Electrical & Inverter",
                "services": [
                    {
                        "name": "House Wiring",
                        "description": (
                            "House wiring, rewiring, electrical point installation, "
                            "and complete residential wiring services."
                        ),
                    },
                    {
                        "name": "Electrical Troubleshooting",
                        "description": (
                            "Diagnosis and solution of electrical faults, short circuits, "
                            "MCB trips, power issues, and other electrical problems."
                        ),
                    },
                    {
                        "name": "Electrical Maintenance",
                        "description": (
                            "Electrical inspection, preventive maintenance, fault checking, "
                            "and general electrical repair services."
                        ),
                    },
                    {
                        "name": "New Electrical Installation",
                        "description": (
                            "Installation of new electrical switches, sockets, lights, "
                            "wiring points, and other electrical equipment."
                        ),
                    },
                    {
                        "name": "Inverter Repair",
                        "description": (
                            "Inverter diagnosis, repair, battery checking, backup testing, "
                            "and inverter maintenance services."
                        ),
                    },
                    {
                        "name": "Battery Runtime Calculator",
                        "description": (
                            "Calculate estimated battery backup runtime based on battery "
                            "capacity, voltage, load, and power consumption."
                        ),
                    },
                ],
            },

            {
                "category": "CCTV & Security",
                "services": [
                    {
                        "name": "CCTV Camera Installation",
                        "description": (
                            "Professional CCTV camera installation, wiring, positioning, "
                            "and complete surveillance system setup."
                        ),
                    },
                    {
                        "name": "CCTV Repair",
                        "description": (
                            "Diagnosis and repair of CCTV cameras, DVR/NVR systems, "
                            "power problems, cabling, and related equipment."
                        ),
                    },
                    {
                        "name": "CCTV Maintenance",
                        "description": (
                            "CCTV system inspection, cleaning, testing, configuration, "
                            "and preventive maintenance."
                        ),
                    },
                    {
                        "name": "Remote Mobile Viewing & NVR Setup",
                        "description": (
                            "NVR configuration and remote CCTV viewing setup for "
                            "mobile phones and other internet-connected devices."
                        ),
                    },
                ],
            },

            {
                "category": "Computer & IT Support",
                "services": [
                    {
                        "name": "Computer Installation",
                        "description": (
                            "Desktop computer setup, operating system installation, "
                            "driver installation, software setup, and configuration."
                        ),
                    },
                    {
                        "name": "Computer Repair",
                        "description": (
                            "Computer hardware and software diagnosis, troubleshooting, "
                            "component replacement, and repair."
                        ),
                    },
                    {
                        "name": "Computer Maintenance",
                        "description": (
                            "Computer cleaning, optimization, hardware inspection, "
                            "software updates, and preventive maintenance."
                        ),
                    },
                    {
                        "name": "Software, Virus & Security Removal",
                        "description": (
                            "Virus and malware removal, unwanted software cleanup, "
                            "security troubleshooting, and system protection setup."
                        ),
                    },
                ],
            },

            {
                "category": "Fan Services",
                "services": [
                    {
                        "name": "Ceiling Fan Installation & Repair",
                        "description": (
                            "Ceiling fan installation, wiring, troubleshooting, "
                            "repair, capacitor replacement, and maintenance."
                        ),
                    },
                    {
                        "name": "Wall Fan Installation & Repair",
                        "description": (
                            "Wall fan installation, wiring, troubleshooting, repair, "
                            "and general maintenance services."
                        ),
                    },
                ],
            },

            {
                "category": "DishHome DTH & TV",
                "services": [
                    {
                        "name": "LED TV Installation",
                        "description": (
                            "LED TV installation, initial setup, cable connection, "
                            "and basic configuration."
                        ),
                    },
                    {
                        "name": "LED TV Repair",
                        "description": (
                            "LED TV diagnosis and repair for display, power, sound, "
                            "software, and other common TV problems."
                        ),
                    },
                    {
                        "name": "TV Wall Mount Bracket Installation",
                        "description": (
                            "Professional wall mounting of LED TVs with secure "
                            "bracket installation and positioning."
                        ),
                    },
                ],
            },

            {
                "category": "Fiber & LAN Networking",
                "services": [
                    {
                        "name": "DishHome Installation",
                        "description": (
                            "DishHome DTH installation, dish alignment, receiver setup, "
                            "and complete connection configuration."
                        ),
                    },
                    {
                        "name": "DishHome Maintenance",
                        "description": (
                            "DishHome troubleshooting, signal checking, dish adjustment, "
                            "receiver inspection, and maintenance."
                        ),
                    },
                    {
                        "name": "Local Networking Setup",
                        "description": (
                            "LAN and local network setup, device connection, "
                            "network configuration, and basic troubleshooting."
                        ),
                    },
                    {
                        "name": "Fiber Drop Wire & Router Configuration",
                        "description": (
                            "Fiber drop wire installation, router configuration, "
                            "internet setup, and basic network optimization."
                        ),
                    },
                ],
            },

            {
                "category": "AC & Refrigeration",
                "services": [
                    {
                        "name": "AC Installation",
                        "description": (
                            "Air conditioner installation, indoor and outdoor unit setup, "
                            "piping, drainage, and electrical connection."
                        ),
                    },
                    {
                        "name": "AC Repair",
                        "description": (
                            "AC diagnosis and repair for cooling, electrical, drainage, "
                            "compressor, and other common problems."
                        ),
                    },
                    {
                        "name": "AC Maintenance",
                        "description": (
                            "Regular AC inspection, preventive maintenance, filter care, "
                            "gas and performance checking."
                        ),
                    },
                    {
                        "name": "Jet Cleaning & Cooling Performance Test",
                        "description": (
                            "Deep jet cleaning and cooling performance testing to improve "
                            "AC cleanliness, airflow, and cooling efficiency."
                        ),
                    },
                ],
            },

            {
                "category": "Plumbing & Sanitary",
                "services": [
                    {
                        "name": "Plumbing Troubleshooting",
                        "description": (
                            "Diagnosis and solution of plumbing problems, blocked pipes, "
                            "water flow issues, leakage, and other sanitary faults."
                        ),
                    },
                    {
                        "name": "Plumbing Maintenance",
                        "description": (
                            "Preventive plumbing maintenance, inspection, repair, "
                            "and general sanitary system servicing."
                        ),
                    },
                    {
                        "name": "Pipe Leakage Repair & Water Tank Fitting",
                        "description": (
                            "Pipe leakage repair, water tank fitting, pipe connections, "
                            "and related plumbing installation services."
                        ),
                    },
                ],
            },
        ]

        total_categories = 0
        total_services = 0

        for category_data in services_data:

            category_name = category_data["category"]

            category, category_created = Category.objects.get_or_create(
                name=category_name
            )

            if category_created:
                total_categories += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created category: {category.name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Category already exists: {category.name}"
                    )
                )

            for service_data in category_data["services"]:

                service, service_created = Service.objects.get_or_create(
                    name=service_data["name"],
                    defaults={
                        "description": service_data["description"],
                        "category": category,
                    },
                )

                if service_created:
                    total_services += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"    Created service: {service.name}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"    Already exists: {service.name}"
                        )
                    )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "========================================"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Service seeding completed successfully."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"New categories created: {total_categories}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"New services created: {total_services}"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "========================================"
            )
        )