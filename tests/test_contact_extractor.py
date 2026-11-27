
import unittest

from src.resume_parser.understanding.contact_extractor import (
    extract_phone_numbers,
    extract_primary_phone,
    extract_address,
)


class TestPhoneExtraction(unittest.TestCase):

    def test_indian_formats(self):
        formats = [
            "(+91) 855 182 6442",
            "+91 855 182 6442",
            "+918551826442",
            "855 182 6442",
            "8551826442",
            "+91-855-182-6442",
            "(91) 8551826442",
        ]

        for value in formats:
            with self.subTest(value=value):
                result = extract_primary_phone(value)
                self.assertEqual(result, "+918551826442")

    def test_invalid_values(self):
        text = """
        Date: 12/05/2025
        PIN: 673101
        """

        self.assertEqual(extract_phone_numbers(text), [])

    def test_duplicate_numbers(self):
        text = """
        Phone: +91 855 182 6442
        Mobile: 8551826442
        """

        self.assertEqual(
            extract_phone_numbers(text),
            ["+918551826442"]
        )


class TestAddressExtraction(unittest.TestCase):

    def test_same_line_address(self):
        text = """
        Janak Ramesh
        Address: Vadakara, Kozhikode
        """

        self.assertEqual(
            extract_address(text),
            "Vadakara, Kozhikode"
        )

    def test_multiline_address(self):
        text = """
        Present Address:
        Vadakara
        Kozhikode, Kerala
        Education
        B.Tech Computer Science
        """

        self.assertEqual(
            extract_address(text),
            "Vadakara, Kozhikode, Kerala"
        )

    def test_missing_address(self):
        text = """
        Janak Ramesh
        Education
        B.Tech Computer Science
        """

        self.assertEqual(extract_address(text), "")

    def test_address_with_social_links(self):
        text = """
        Janak Ramesh
        janakramesh2003@gmail.com — +91 9400738640
        LinkedIn — GitHub — Vadakara, Kozhikode
        PROFESSIONAL SUMMARY
        B.Tech Computer Science graduate
        """

        self.assertEqual(
            extract_address(text),
            "Vadakara, Kozhikode"
        )

    def test_standalone_header_address(self):
        text = """
        OLIVER DAVIS
        Senior Consultant | ETL Expert | PySpark Specialist
        (234)-555-1234
        linkedin.com
        Columbus, Ohio
        SUMMARY
        Seasoned consultant with experience.
        """

        self.assertEqual(
            extract_address(text),
            "Columbus, Ohio"
        )

    def test_does_not_extract_experience_location(self):
        text = """
        OLIVER DAVIS
        Senior Consultant
        SUMMARY
        Experienced consultant.
        EXPERIENCE
        Data Integration Architect
        Cognizant
        Mar 2019 - Present
        Columbus, Ohio
        """

        self.assertEqual(extract_address(text), "")

    def test_labelled_address_still_works(self):
        text = """
        Name: John
        Present Address: Hyderabad, Telangana
        EDUCATION
        Bachelor of Technology
        """

        self.assertEqual(
            extract_address(text),
            "Hyderabad, Telangana"
        )

    def test_address_keyword_inside_personal_details(self):
        text = """
        JOHN DAVIS
        PERSONAL DETAILS
        Present Address:
        Flat 204, Green Residency
        Kukatpally, Hyderabad, Telangana
        Permanent Address:
        Kochi, Kerala
        """

        self.assertEqual(
            extract_address(text),
            "Kochi, Kerala"
        )

    def test_address_keyword_after_experience(self):
        text = """
        JOHN DAVIS
        EXPERIENCE
        Python Developer
        ABC Technologies

        CURRENT ADDRESS: Hyderabad, Telangana
        """

        self.assertEqual(
            extract_address(text),
            "Hyderabad, Telangana"
        )

    def test_prefers_permanent_address_over_present_address(self):
        text = """
        Present Address: 401 Tamkeen Towers, Al Khan Street, Sharjah (UAE)
        Permanent Address: G-401, Kubhera Vistas, Saravanampatti,
        Coimbatore 641035 [IN]
        """

        self.assertEqual(
            extract_address(text),
            "G-401, Kubhera Vistas, Saravanampatti, Coimbatore 641035 [IN]"
        )

    def test_address_label_on_later_page(self):
        text = """
        SUMMARY
        Experienced technology leader.
        --- PAGE 4 ---
        PERSONAL DETAILS
        Residential Address: Flat 12, Rose Residency
        """

        self.assertEqual(
            extract_address(text),
            "Flat 12, Rose Residency"
        )

    def test_multiline_address_stops_at_other_fields(self):
        text = """
        Present Address:
        Apartment 12, Building 4
        Al Khan Street
        Sharjah 641035 [UAE]
        Phone: +91 855 182 6442
        Email: jane@example.com
        """

        self.assertEqual(
            extract_address(text),
            "Apartment 12, Building 4, Al Khan Street, Sharjah 641035 [UAE]"
        )

    def test_labelled_address_without_commas(self):
        text = """
        Current Address: Flat 4B 2nd Floor 12 Oak Street Springfield 62704 US
        """

        self.assertEqual(
            extract_address(text),
            "Flat 4B 2nd Floor 12 Oak Street Springfield 62704 US"
        )

    def test_rejects_percentage_sentence(self):
        text = """
        PERSONAL DETAILS
        100% focus on his Job.
        """

        self.assertEqual(extract_address(text), "")

    def test_ignores_company_and_education_locations(self):
        text = """
        EXPERIENCE
        Data Integration Architect
        Infotech, US
        EDUCATION
        University of Example
        Columbus, Ohio
        ACHIEVEMENTS
        Infotech, US
        """

        self.assertEqual(extract_address(text), "")

    def test_address_label_near_other_contact_information(self):
        text = (
            "Jane Doe\n"
            "Email: jane@example.com | Phone: +1 555 123 4567 | "
            "Present Address: 12 Oak Street, Springfield\n"
            "SUMMARY\n"
            "Technology leader."
        )

        self.assertEqual(
            extract_address(text),
            "12 Oak Street, Springfield"
        )

    def test_unlabelled_address_uses_only_resume_header(self):
        text = """
        Oliver Davis
        Columbus, Ohio
        SUMMARY
        Technology leader.
        EXPERIENCE
        Infotech, US
        """

        self.assertEqual(extract_address(text), "Columbus, Ohio")

    def test_unlabelled_company_location_in_later_section_is_ignored(self):
        text = """
        Oliver Davis
        SUMMARY
        Technology leader.
        EXPERIENCE
        Infotech, US
        """

        self.assertEqual(extract_address(text), "")

    def test_permanent_label_has_priority_when_addresses_are_reversed(self):
        text = """
        Current Address: 22 Lake View Apartment, Block 3
        Permanent Address: 8 Garden Lane, Coimbatore 641035 [IN]
        Present Address: 401 Tamkeen Towers, Sharjah (UAE)
        """

        self.assertEqual(
            extract_address(text),
            "8 Garden Lane, Coimbatore 641035 [IN]"
        )


if __name__ == "__main__":
    unittest.main()
