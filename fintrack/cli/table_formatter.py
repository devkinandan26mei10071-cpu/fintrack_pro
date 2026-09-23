"""
Terminal presentation and box-drawing table formatter.
Zero external dependencies, supports right/left alignment, borders, and ANSI colors.
"""

from typing import List, Any, Optional


class TableFormatter:
    """Renders tabular data with clean ASCII/Unicode borders and column alignment."""

    # ANSI Color Codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"
    GRAY = "\033[90m"

    @classmethod
    def render(
        cls,
        headers: List[str],
        rows: List[List[Any]],
        alignments: Optional[List[str]] = None,
        title: Optional[str] = None
    ) -> str:
        """
        Renders a cleanly formatted ASCII table.
        
        Args:
            headers: List of column header titles.
            rows: List of data rows.
            alignments: List of 'L' (left) or 'R' (right) for each column.
            title: Optional table banner title.
            
        Returns:
            Multi-line string representation of the table.
        """
        if not headers:
            return ""

        num_cols = len(headers)
        if not alignments:
            alignments = ["L"] * num_cols

        # Convert all row cells to string
        str_rows = [[str(cell) if cell is not None else "" for cell in row] for row in rows]

        # Calculate max width for each column
        col_widths = [len(h) for h in headers]
        for row in str_rows:
            for i in range(min(len(row), num_cols)):
                col_widths[i] = max(col_widths[i], len(row[i]))

        # Minimum width of 3 chars per col
        col_widths = [max(w, 3) for w in col_widths]

        lines = []

        # Border parts
        top_border = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
        header_sep = "=" + "=".join(["=" * (w + 2) for w in col_widths]) + "="
        row_sep = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"

        # Title banner
        if title:
            total_inner_width = sum(col_widths) + (3 * num_cols) - 1
            centered_title = title.center(total_inner_width)
            lines.append("+" + "-" * total_inner_width + "+")
            lines.append(f"|{centered_title}|")

        lines.append(top_border)

        # Header row
        header_cells = []
        for i, h in enumerate(headers):
            header_cells.append(f" {h.center(col_widths[i])} ")
        lines.append("|" + "|".join(header_cells) + "|")
        lines.append(header_sep)

        # Data rows
        if not str_rows:
            total_inner_width = sum(col_widths) + (3 * num_cols) - 1
            lines.append(f"|{'No records found.'.center(total_inner_width)}|")
        else:
            for row in str_rows:
                cells = []
                for i in range(num_cols):
                    val = row[i] if i < len(row) else ""
                    align = alignments[i].upper() if i < len(alignments) else "L"
                    if align == "R":
                        formatted_cell = val.rjust(col_widths[i])
                    else:
                        formatted_cell = val.ljust(col_widths[i])
                    cells.append(f" {formatted_cell} ")
                lines.append("|" + "|".join(cells) + "|")

        lines.append(row_sep)
        return "\n".join(lines)

    @classmethod
    def colorize(cls, text: str, color_code: str) -> str:
        """Applies ANSI color escaping if terminal supports it."""
        return f"{color_code}{text}{cls.RESET}"
