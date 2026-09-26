from django.core.management.base import BaseCommand
from api.models import Service, Category


class Command(BaseCommand):
    help = "Create default services"

    def handle(self, *args, **kwargs):

        services = [
            {
                "name": "Electrical & Wiring",
                "description": (
                    "Short-circuit fixes, house rewiring, MCB trip diagnostics, "
                    "and lighting setups by licensed electricians."
                ),
                "category": "Electrical"
            },
            {
                "name": "Plumbing & Sanitary",
                "description": (
                    "Pipe leaks, motor pump repairs, bathroom fitting installs, "
                    "and overhead tank cleaning solutions."
                ),
                "category": "Plumbing"
            },
            {
                "name": "CCTV & Security",
                "description": (
                    "HD/IP surveillance camera setups, NVR configuration, "
                    "remote phone view setup, and maintenance."
                ),
                "category": "Security"
            },
            {
                "name": "Internet & WiFi Support",
                "description": (
                    "Fiber line splicing, router range extension, dual-band setup, "
                    "and commercial LAN cabling."
                ),
                "category": "Networking"
            },
            {
                "name": "Laptop & Computer Clinic",
                "description": (
                    "Windows/Mac troubleshooting, SSD upgrades, chip-level "
                    "motherboard repair, and virus cleanups."
                ),
                "category": "Computer Repair"
            },
            {
                "name": "Inverter & Solar Power",
                "description": (
                    "Battery health checks, solar inverter troubleshooting, "
                    "backup wiring, and seasonal maintenance."
                ),
                "category": "Solar"
            },
        ]


        for item in services:

            category_name = item.pop("category")

            category, created = Category.objects.get_or_create(
                name=category_name
            )

            service, created = Service.objects.get_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "category": category,
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {service.name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Already exists: {service.name}"
                    )
                )


        self.stdout.write(
            self.style.SUCCESS(
                "Service seeding completed successfully."
            )
        )