from src.suite_generator import TestCase


class OutputFormatter:
    def format_test_cases(self, test_cases: list[TestCase], title: str) -> str:
        """Format a list of test cases into Markdown."""
        md = f"# {title}\n\n"
        if not test_cases:
            md += "No test cases generated.\n"
        else:
            for tc in test_cases:
                md += f"## {tc.id}: {tc.title}\n"
                md += f"- **Module:** {tc.module}\n"
                md += f"- **Priority:** {tc.priority}\n"
                md += f"- **Type:** {tc.type}\n"
                md += "- **Prerequisites:**\n"
                for prereq in tc.prerequisites:
                    md += f"  - {prereq}\n"
                md += "- **Steps:**\n"
                for step in tc.steps:
                    md += f"  - {step}\n"
                md += "- **Expected Results:**\n"
                for result in tc.expected_results:
                    md += f"  - {result}\n"
                md += "\n"
        return md

    def format_additional_test_cases(self, gaps_with_tests: list[dict]) -> str:
        """Format additional test cases grouped by gap into Markdown."""
        md = "# Additional Tests for Gaps\n\n"
        if not gaps_with_tests:
            md += "No additional tests needed.\n"
        else:
            for item in gaps_with_tests:
                gap = item["gap"]
                tests = item["tests"]
                md += f"## Gap: {gap['description']}\n"
                md += f"- **Suggested Clarification:** {gap['suggested_clarification']}\n"
                md += f"- **Confidence Level:** {gap['confidence_level']}\n\n"
                for tc in tests:
                    md += f"### {tc.id}: {tc.title}\n"
                    md += f"- **Module:** {tc.module}\n"
                    md += f"- **Priority:** {tc.priority}\n"
                    md += f"- **Type:** {tc.type}\n"
                    md += "- **Prerequisites:**\n"
                    for prereq in tc.prerequisites:
                        md += f"  - {prereq}\n"
                    md += "- **Steps:**\n"
                    for step in tc.steps:
                        md += f"  - {step}\n"
                    md += "- **Expected Results:**\n"
                    for result in tc.expected_results:
                        md += f"  - {result}\n"
                    md += "\n"
        return md

    def format_gap_analysis(self, gaps_with_tests: list[dict]) -> str:
        """Format gap analysis findings into Markdown."""
        md = "# Gap Analysis\n\n"
        if not gaps_with_tests:
            md += "No gaps identified.\n"
        else:
            for i, item in enumerate(gaps_with_tests, start=1):
                gap = item["gap"]
                related_tests = [tc.id for tc in item["tests"]]
                md += f"## Gap {i}\n"
                md += f"- **Description:** {gap['description']}\n"
                md += f"- **Suggested Clarification:** {gap['suggested_clarification']}\n"
                md += f"- **Confidence Level:** {gap['confidence_level']}\n"
                if related_tests:
                    md += (
                        "- **Related Test Cases:** "
                        + ", ".join(related_tests)
                        + "\n"
                    )
                else:
                    md += "- **Related Test Cases:** None\n"
                md += "\n"
        return md
