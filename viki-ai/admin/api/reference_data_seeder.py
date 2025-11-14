#!/usr/bin/env python3
"""
Reference Data Seeder Script

This script seeds the admin_ref_lists collection in Firestore with business units and solutions data.
Run this script after setting up the new reference lists functionality.

Usage:
    python reference_data_seeder.py
"""

import asyncio
import json
from datetime import datetime
from google.cloud.firestore import AsyncClient

# Business units data (from the original hardcoded data)
BUSINESS_UNITS = [
    {"bu_code": "wsh", "name": "WS Home"},
    {"bu_code": "pac", "name": "Post Acute Care"},
    {"bu_code": "pacf", "name": "Post Acute Care Facilities"},
    {"bu_code": "hss", "name": "Human and Social Services"},
    {"bu_code": "bm", "name": "Blood Management"},
    {"bu_code": "cp", "name": "CarePort"},
    {"bu_code": "pe", "name": "Healthify"},
]

# Solutions data (from the original hardcoded data)
SOLUTIONS = [
    {
        "solution_id": "hp-wsh-001",
        "code": "hp",
        "name": "Hospice and Palliative (Consolo)",
        "description": "Hospice and Palliative Care Management System",
        "bu_code": "wsh"
    },
    {
        "solution_id": "hh-wsh-001",
        "code": "hh",
        "name": "Home Health and Hospice",
        "description": "Home Health and Hospice Management System",
        "bu_code": "wsh"
    },
    {
        "solution_id": "pc-wsh-001",
        "code": "pc",
        "name": "Personal Care",
        "description": "Personal Care Management System",
        "bu_code": "wsh"
    },
    {
        "solution_id": "ct-pac-001",
        "code": "ct",
        "name": "CareTend",
        "description": "Post Acute Care Management System",
        "bu_code": "pac"
    },
    {
        "solution_id": "cpr-pac-001",
        "code": "cpr",
        "name": "CPR Plus",
        "description": "Enhanced Post Acute Care System",
        "bu_code": "pac"
    },
    {
        "solution_id": "sc-pacf-001",
        "code": "sc",
        "name": "Specialty Care",
        "description": "Specialty Care Management System",
        "bu_code": "pacf"
    },
    {
        "solution_id": "ads-pacf-001",
        "code": "ads",
        "name": "WellSky Adult Day",
        "description": "Adult Day Services Management System",
        "bu_code": "pacf"
    },
    {
        "solution_id": "wsr-pacf-001",
        "code": "wsr",
        "name": "WellSky Rehab",
        "description": "Rehabilitation Services Management System",
        "bu_code": "pacf"
    },
    {
        "solution_id": "hs-hss-001",
        "code": "hs",
        "name": "Human Services",
        "description": "Human Services Management System",
        "bu_code": "hss"
    },
    {
        "solution_id": "cs-hss-001",
        "code": "cs",
        "name": "Community Services",
        "description": "Community Services Management System",
        "bu_code": "hss"
    },
    {
        "solution_id": "ad-hss-001",
        "code": "ad",
        "name": "Aging and Disability (SAMS)",
        "description": "State Agency Management System for Aging and Disability",
        "bu_code": "hss"
    },
    {
        "solution_id": "bh-hss-001",
        "code": "bh",
        "name": "Behavioral Health and IDD Providers",
        "description": "Behavioral Health and Intellectual/Developmental Disabilities System",
        "bu_code": "hss"
    },
    {
        "solution_id": "biotl-bm-001",
        "code": "biotl",
        "name": "Biotherapies Lab",
        "description": "Biotherapies Laboratory Management System",
        "bu_code": "bm"
    },
    {
        "solution_id": "biotc-bm-001",
        "code": "biotc",
        "name": "Biotherapies Clinic",
        "description": "Biotherapies Clinic Management System",
        "bu_code": "bm"
    },
    {
        "solution_id": "bc-bm-001",
        "code": "bc",
        "name": "Blood Center",
        "description": "Blood Center Management System",
        "bu_code": "bm"
    },
    {
        "solution_id": "blood-bm-001",
        "code": "blood",
        "name": "Blood Transfusion",
        "description": "Blood Transfusion Management System",
        "bu_code": "bm"
    },
    {
        "solution_id": "cpci-cp-001",
        "code": "cpci",
        "name": "Connect / Insight",
        "description": "Care Coordination Connect and Insight Platform",
        "bu_code": "cp"
    },
    {
        "solution_id": "cpcm-cp-001",
        "code": "cpcm",
        "name": "Care Management",
        "description": "Care Management Platform",
        "bu_code": "cp"
    },
    {
        "solution_id": "scc-pe-001",
        "code": "scc",
        "name": "Social Care Coordination",
        "description": "Social Care Coordination System",
        "bu_code": "pe"
    },
    {
        "solution_id": "cc-pe-001",
        "code": "cc",
        "name": "Care Coordination",
        "description": "Care Coordination System",
        "bu_code": "pe"
    },
]


async def seed_business_units(client: AsyncClient):
    """Seed business units data to Firestore."""
    try:
        collection_ref = client.collection("admin_ref_lists")
        doc_ref = collection_ref.document("bus")

        data = {
            "business_units": BUSINESS_UNITS,
            "created_at": datetime.utcnow(),
            "created_by": "seeder_script",
            "updated_at": datetime.utcnow(),
            "updated_by": "seeder_script",
        }

        await doc_ref.set(data)
        print(f"✅ Successfully seeded {len(BUSINESS_UNITS)} business units")

    except Exception as e:
        print(f"❌ Error seeding business units: {str(e)}")
        raise


async def seed_solutions(client: AsyncClient):
    """Seed solutions data to Firestore."""
    try:
        collection_ref = client.collection("admin_ref_lists")
        doc_ref = collection_ref.document("solutions")

        data = {
            "solutions": SOLUTIONS,
            "created_at": datetime.utcnow(),
            "created_by": "seeder_script",
            "updated_at": datetime.utcnow(),
            "updated_by": "seeder_script",
        }

        await doc_ref.set(data)
        print(f"✅ Successfully seeded {len(SOLUTIONS)} solutions")

    except Exception as e:
        print(f"❌ Error seeding solutions: {str(e)}")
        raise


async def verify_data(client: AsyncClient):
    """Verify that the data was seeded correctly."""
    try:
        collection_ref = client.collection("admin_ref_lists")

        # Verify business units
        bus_doc = await collection_ref.document("bus").get()
        if bus_doc.exists:
            bus_data = bus_doc.to_dict()
            bus_count = len(bus_data.get("business_units", []))
            print(f"✅ Verified business units: {bus_count} entries found")
        else:
            print("❌ Business units document not found")

        # Verify solutions
        solutions_doc = await collection_ref.document("solutions").get()
        if solutions_doc.exists:
            solutions_data = solutions_doc.to_dict()
            solutions_count = len(solutions_data.get("solutions", []))
            print(f"✅ Verified solutions: {solutions_count} entries found")
        else:
            print("❌ Solutions document not found")

    except Exception as e:
        print(f"❌ Error verifying data: {str(e)}")
        raise


async def main():
    """Main function to seed reference data."""
    print("🚀 Starting reference data seeding...")

    # Initialize Firestore client
    client = AsyncClient()

    try:
        # Seed business units
        print("\n📋 Seeding business units...")
        await seed_business_units(client)

        # Seed solutions
        print("\n🔧 Seeding solutions...")
        await seed_solutions(client)

        # Verify data
        print("\n✅ Verifying seeded data...")
        await verify_data(client)

        print("\n🎉 Reference data seeding completed successfully!")
        print("\nNext steps:")
        print("1. Start the Admin API server")
        print("2. Test the new endpoints:")
        print("   - GET /api/v1/reference-lists/business-units")
        print("   - GET /api/v1/reference-lists/solutions")
        print("   - GET /api/v1/reference-lists/all")
        print("3. Check the frontend components to ensure they load dynamic data")

    except Exception as e:
        print(f"\n💥 Seeding failed: {str(e)}")
        return 1

    finally:
        await client.close()

    return 0


if __name__ == "__main__":
    asyncio.run(main())