"""
Python Data Visualization Project Using Matplotlib
---------------------------------------------------
Name         : Muhammad Saqlain
Registration : 2024-KIU-BS5408
Program      : BS Data Science

What this script does:
    1. Creates my own sales dataset (4 products x 6 months) and saves it as a CSV
    2. Reads the data back and calculates some basic numbers
    3. Draws 4 charts (line, bar, pie, multiple line) and saves each as PNG
    4. Draws all of them together in one figure using subplots
    5. Builds a PDF report (dataset + charts + analysis) using Matplotlib's PdfPages

Run it with:   python sales_analysis.py
"""

import csv
import os
import textwrap

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# ------------------------------------------------------------------
# Folder setup
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
CHART_DIR = os.path.join(BASE_DIR, "charts")
REPORT_DIR = os.path.join(BASE_DIR, "report")

for folder in (DATA_DIR, CHART_DIR, REPORT_DIR):
    os.makedirs(folder, exist_ok=True)

CSV_PATH = os.path.join(DATA_DIR, "sales_data.csv")
PDF_PATH = os.path.join(REPORT_DIR, "Sales_Analysis_Report.pdf")

# ------------------------------------------------------------------
# Step 1: My own dataset (units sold per month, Jan - Jun 2026)
# Imagine a small electronics shop selling these 4 products
# ------------------------------------------------------------------
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]

sales_dict = {
    "Laptops":      [120, 135, 150, 142, 165, 180],
    "Smartphones":  [210, 225, 198, 240, 260, 285],
    "Headphones":   [340, 310, 355, 390, 375, 420],
    "Smartwatches": [85, 92, 110, 125, 140, 170],
}

# one colour + one marker for each product so they look the same in every chart
colors = {
    "Laptops": "#1f77b4",
    "Smartphones": "#ff7f0e",
    "Headphones": "#2ca02c",
    "Smartwatches": "#d62728",
}
markers = {
    "Laptops": "o",
    "Smartphones": "s",
    "Headphones": "^",
    "Smartwatches": "D",
}


def save_dataset_to_csv():
    """Write the dataset into a CSV file (rows = months, columns = products)."""
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Month"] + list(sales_dict.keys()))
        for i, m in enumerate(months):
            writer.writerow([m] + [sales_dict[p][i] for p in sales_dict])


def load_dataset_from_csv():
    """Read the CSV back so the charts really use the file data."""
    data = {}
    month_list = []
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        products = [c for c in reader.fieldnames if c != "Month"]
        for p in products:
            data[p] = []
        for row in reader:
            month_list.append(row["Month"])
            for p in products:
                data[p].append(int(row[p]))
    return month_list, data


save_dataset_to_csv()
months, sales = load_dataset_from_csv()
products = list(sales.keys())

# ------------------------------------------------------------------
# Step 2: Basic calculations
# ------------------------------------------------------------------
monthly_total = [sum(sales[p][i] for p in products) for i in range(len(months))]
product_total = {p: sum(sales[p]) for p in products}
grand_total = sum(product_total.values())
share = {p: product_total[p] / grand_total * 100 for p in products}
avg_monthly = {p: product_total[p] / len(months) for p in products}
growth = {p: (sales[p][-1] - sales[p][0]) / sales[p][0] * 100 for p in products}

best_month_idx = monthly_total.index(max(monthly_total))
worst_month_idx = monthly_total.index(min(monthly_total))
top_product = max(product_total, key=product_total.get)
low_product = min(product_total, key=product_total.get)
fastest_product = max(growth, key=growth.get)
slowest_product = min(growth, key=growth.get)

print("Monthly totals :", dict(zip(months, monthly_total)))
print("Product totals :", product_total)
print("Grand total    :", grand_total)


# ------------------------------------------------------------------
# Step 3: Chart functions
# Each function draws on the axes it receives, so I can reuse the
# same code for the single PNG charts and for the subplot figure.
# ------------------------------------------------------------------
def draw_line_chart(ax):
    """Line chart - total monthly sales trend of the whole shop."""
    ax.plot(months, monthly_total, color="#4c72b0", marker="o", markersize=8,
            linewidth=2.5, label="Total Units Sold")
    # write the value above every point
    for x, y in zip(months, monthly_total):
        ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=9)
    ax.set_title("Monthly Sales Trend (All Products)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Month (2026)")
    ax.set_ylabel("Units Sold")
    ax.set_ylim(min(monthly_total) - 100, max(monthly_total) + 120)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")


def draw_bar_chart(ax):
    """Bar chart - total 6-month sales of each product."""
    totals = [product_total[p] for p in products]
    bars = ax.bar(products, totals, color=[colors[p] for p in products],
                  edgecolor="black", width=0.6)
    for bar, val in zip(bars, totals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 25, str(val),
                ha="center", fontsize=10, fontweight="bold")
    ax.set_title("Product-wise Total Sales (Jan - Jun)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Product")
    ax.set_ylabel("Total Units Sold")
    ax.set_ylim(0, max(totals) + 300)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(bars, products, title="Products", loc="upper left", fontsize=8)


def draw_pie_chart(ax):
    """Pie chart - percentage contribution of each product."""
    totals = [product_total[p] for p in products]
    explode = [0.06 if p == top_product else 0 for p in products]  # pull out the best seller
    wedges, texts, autotexts = ax.pie(
        totals, labels=products, colors=[colors[p] for p in products],
        autopct="%1.1f%%", startangle=90, explode=explode,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 10})
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("Percentage Contribution of Each Product", fontsize=13, fontweight="bold")
    ax.legend(wedges, products, title="Products", loc="lower left",
              bbox_to_anchor=(-0.15, -0.1), fontsize=8)


def draw_multi_line_chart(ax):
    """Multiple line chart - all products compared over 6 months."""
    for p in products:
        ax.plot(months, sales[p], color=colors[p], marker=markers[p],
                markersize=7, linewidth=2, label=p)
    ax.set_title("Product Sales Comparison Over 6 Months", fontsize=13, fontweight="bold")
    ax.set_xlabel("Month (2026)")
    ax.set_ylabel("Units Sold")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(title="Products", loc="upper left", ncol=2, fontsize=9)
    ax.set_ylim(0, max(max(v) for v in sales.values()) + 150)


def save_single_chart(draw_func, filename, figsize=(9, 6)):
    """Draw one chart alone in its own figure and save as PNG."""
    fig, ax = plt.subplots(figsize=figsize)
    draw_func(ax)
    fig.tight_layout()
    path = os.path.join(CHART_DIR, filename)
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print("Saved:", path)
    return path


# ------------------------------------------------------------------
# Step 4: Generate and save all charts
# ------------------------------------------------------------------
line_png = save_single_chart(draw_line_chart, "1_line_chart_monthly_trend.png")
bar_png = save_single_chart(draw_bar_chart, "2_bar_chart_product_sales.png")
pie_png = save_single_chart(draw_pie_chart, "3_pie_chart_contribution.png", figsize=(8, 7))
multi_png = save_single_chart(draw_multi_line_chart, "4_multiple_line_chart.png")

# All 4 charts together using subplots (2 x 2)
fig, axes = plt.subplots(2, 2, figsize=(15, 11))
draw_line_chart(axes[0, 0])
draw_bar_chart(axes[0, 1])
draw_pie_chart(axes[1, 0])
draw_multi_line_chart(axes[1, 1])
fig.suptitle("Sales Dashboard - Electronics Shop (Jan to Jun 2026)",
             fontsize=18, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.96])
subplot_png = os.path.join(CHART_DIR, "5_subplots_dashboard.png")
fig.savefig(subplot_png, dpi=200)
plt.close(fig)
print("Saved:", subplot_png)

# ------------------------------------------------------------------
# Step 5: Written analysis (numbers come from the calculations above)
# ------------------------------------------------------------------
m = months
analysis = {
    "1. Overall sales trend": (
        f"Total sales of the shop went up from {monthly_total[0]} units in {m[0]} to "
        f"{monthly_total[-1]} units in {m[-1]}, which is a rise of "
        f"{(monthly_total[-1] - monthly_total[0]) / monthly_total[0] * 100:.1f}%. "
        f"{m[best_month_idx]} was the best month ({monthly_total[best_month_idx]} units) and "
        f"{m[worst_month_idx]} was the weakest ({monthly_total[worst_month_idx]} units). "
        f"The line chart shows that growth was slow in the first two months and then became "
        f"much faster from March onwards. Over the 6 months the shop sold {grand_total} units "
        f"in total, about {grand_total / len(months):.0f} units per month on average."
    ),
    "2. Product-wise comparison": (
        f"{top_product} was the best-selling product with {product_total[top_product]} units "
        f"({share[top_product]:.1f}% of all sales). Smartphones came second with "
        f"{product_total['Smartphones']} units ({share['Smartphones']:.1f}%). "
        f"Laptops sold {product_total['Laptops']} units ({share['Laptops']:.1f}%) and "
        f"{low_product} were the lowest with {product_total[low_product]} units "
        f"({share[low_product]:.1f}%). Headphones and Smartphones together make up more than "
        f"two thirds of the total sales, so the shop depends a lot on these two products."
    ),
    "3. Growth of each product": (
        f"{fastest_product} had the fastest growth. They went from {sales[fastest_product][0]} "
        f"units in {m[0]} to {sales[fastest_product][-1]} units in {m[-1]}, which is "
        f"{growth[fastest_product]:.0f}% growth, so their sales doubled. Laptops grew by "
        f"{growth['Laptops']:.0f}%, Smartphones by {growth['Smartphones']:.0f}% and "
        f"{slowest_product} by {growth[slowest_product]:.0f}%. Headphones sell the most, but "
        f"they are growing the slowest, so the gap between Headphones and the other products "
        f"is becoming smaller."
    ),
    "4. Ups and downs": (
        f"Some products did not grow in a straight line. Laptops dropped from "
        f"{sales['Laptops'][2]} to {sales['Laptops'][3]} units in April, Smartphones dropped "
        f"from {sales['Smartphones'][1]} to {sales['Smartphones'][2]} in March, and Headphones "
        f"dropped from {sales['Headphones'][0]} to {sales['Headphones'][1]} in February and "
        f"from {sales['Headphones'][3]} to {sales['Headphones'][4]} in May before recovering. "
        f"The multiple line chart makes these small dips easy to see. "
        f"Smartwatches were the only product that increased every single month."
    ),
    "5. Conclusion": (
        f"The data shows that the shop is doing well and is growing every month overall. "
        f"Headphones are the main income source, Smartphones are stable, and Smartwatches are "
        f"the most promising product because of their fast growth. If I was the shop owner, I "
        f"would keep enough stock of Headphones and Smartphones, and I would put more "
        f"advertising on Smartwatches and Laptops to push their sales even higher. "
        f"A limitation of this study is that it uses only 6 months of data, so it is not "
        f"possible to say whether the pattern is seasonal or not."
    ),
}


# ------------------------------------------------------------------
# Step 6: PDF report (made only with Matplotlib, using PdfPages)
# A4 size in inches = 8.27 x 11.69
# ------------------------------------------------------------------
A4 = (8.27, 11.69)


def new_page():
    """Blank A4 page where I can write text with figure coordinates."""
    page = plt.figure(figsize=A4)
    return page


def add_page_footer(page, number):
    page.text(0.5, 0.025, f"Muhammad Saqlain  |  2024-KIU-BS5408  |  Page {number}",
              ha="center", fontsize=8, color="gray")


def write_paragraph(page, text, y, size=10.5, width=88, x=0.09, line_gap=0.0225, bold=False):
    """Wrap the text and write it line by line. Returns the new y position."""
    for line in textwrap.wrap(text, width=width):
        page.text(x, y, line, fontsize=size, va="top",
                  fontweight="bold" if bold else "normal")
        y -= line_gap
    return y


def chart_page(pdf, png_path, heading, caption, number, landscape_img=True):
    page = new_page()
    page.text(0.5, 0.94, heading, ha="center", fontsize=16, fontweight="bold")
    img = plt.imread(png_path)
    h, w = img.shape[0], img.shape[1]
    # fit the image inside the page width
    img_w = 0.84
    img_h = img_w * (h / w) * (A4[0] / A4[1])
    ax = page.add_axes([0.08, 0.88 - img_h, img_w, img_h])
    ax.imshow(img)
    ax.axis("off")
    y = 0.88 - img_h - 0.04
    page.text(0.09, y, "Description:", fontsize=11, fontweight="bold", va="top")
    write_paragraph(page, caption, y - 0.03, size=10.5)
    add_page_footer(page, number)
    pdf.savefig(page)
    plt.close(page)


with PdfPages(PDF_PATH) as pdf:
    # ---------------- Page 1: title + introduction ----------------
    page = new_page()
    page.text(0.5, 0.93, "Python Data Visualization Project", ha="center",
              fontsize=22, fontweight="bold")
    page.text(0.5, 0.89, "Monthly Sales Analysis Using Matplotlib", ha="center",
              fontsize=15, color="#444444")
    page.text(0.5, 0.82, "Submitted by:  Muhammad Saqlain", ha="center", fontsize=12)
    page.text(0.5, 0.795, "Registration No:  2024-KIU-BS5408", ha="center", fontsize=12)
    page.text(0.5, 0.77, "Program:  BS Data Science", ha="center", fontsize=12)

    y = 0.70
    page.text(0.09, y, "1. Introduction", fontsize=14, fontweight="bold")
    y -= 0.035
    y = write_paragraph(page,
        "In this project I analysed the monthly sales of a small electronics shop. "
        "I made my own dataset for 4 products (Laptops, Smartphones, Headphones and "
        "Smartwatches) for 6 months, from January to June 2026. The numbers are the units "
        "sold in each month. All the calculations and all the charts in this report were "
        "created with Python and Matplotlib.", y)
    y -= 0.03
    page.text(0.09, y, "2. Tools Used", fontsize=14, fontweight="bold")
    y -= 0.035
    for item in ["Python 3 (inside a virtual environment, venv)",
                 "Matplotlib (pyplot, subplots, PdfPages)",
                 "csv and os modules from the Python standard library"]:
        page.text(0.11, y, "-  " + item, fontsize=10.5, va="top")
        y -= 0.025
    y -= 0.025
    page.text(0.09, y, "3. Charts Included in this Report", fontsize=14, fontweight="bold")
    y -= 0.035
    for item in ["Line Chart - monthly sales trend of all products together",
                 "Bar Chart - product-wise total sales",
                 "Pie Chart - percentage contribution of each product",
                 "Multiple Line Chart - all products compared over 6 months",
                 "Subplots - all 4 charts in one figure"]:
        page.text(0.11, y, "-  " + item, fontsize=10.5, va="top")
        y -= 0.025
    y -= 0.025
    page.text(0.09, y, "4. Project Files", fontsize=14, fontweight="bold")
    y -= 0.035
    for item in ["sales_analysis.py - complete source code",
                 "data/sales_data.csv - the dataset",
                 "charts/ - all charts saved as PNG images",
                 "report/Sales_Analysis_Report.pdf - this report"]:
        page.text(0.11, y, "-  " + item, fontsize=10.5, va="top")
        y -= 0.025
    add_page_footer(page, 1)
    pdf.savefig(page)
    plt.close(page)

    # ---------------- Page 2: dataset table ----------------
    page = new_page()
    page.text(0.5, 0.94, "Dataset: Monthly Sales (Units Sold)", ha="center",
              fontsize=16, fontweight="bold")
    page.text(0.09, 0.90,
              "This is the dataset I created myself. Each row is a month and each column "
              "is a product. The last row and the last column are totals.",
              fontsize=10, va="top", wrap=True)

    ax = page.add_axes([0.08, 0.50, 0.84, 0.36])
    ax.axis("off")
    header = ["Month"] + products + ["Total"]
    rows = []
    for i, mon in enumerate(months):
        rows.append([mon] + [str(sales[p][i]) for p in products] + [str(monthly_total[i])])
    rows.append(["Total"] + [str(product_total[p]) for p in products] + [str(grand_total)])
    table = ax.table(cellText=rows, colLabels=header, loc="upper center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.9)
    for col in range(len(header)):
        table[0, col].set_facecolor("#4c72b0")
        table[0, col].set_text_props(color="white", fontweight="bold")
        table[len(rows), col].set_facecolor("#e8e8e8")
        table[len(rows), col].set_text_props(fontweight="bold")

    # summary table of the calculated values
    page.text(0.09, 0.45, "Summary of calculated values", fontsize=13, fontweight="bold")
    ax2 = page.add_axes([0.08, 0.22, 0.84, 0.21])
    ax2.axis("off")
    header2 = ["Product", "Total Units", "Share (%)", "Avg / Month", "Jan to Jun Growth"]
    rows2 = [[p, str(product_total[p]), f"{share[p]:.1f}", f"{avg_monthly[p]:.1f}",
              f"{growth[p]:.1f}%"] for p in products]
    table2 = ax2.table(cellText=rows2, colLabels=header2, loc="upper center", cellLoc="center")
    table2.auto_set_font_size(False)
    table2.set_fontsize(9.5)
    table2.scale(1, 1.9)
    for col in range(len(header2)):
        table2[0, col].set_facecolor("#55a868")
        table2[0, col].set_text_props(color="white", fontweight="bold")
    page.text(0.09, 0.15, "The dataset is also saved as data/sales_data.csv in the project folder.",
              fontsize=9.5, style="italic")
    add_page_footer(page, 2)
    pdf.savefig(page)
    plt.close(page)

    # ---------------- Chart pages ----------------
    chart_page(pdf, line_png, "Chart 1: Line Chart - Monthly Sales Trend",
               "This line chart shows the total units sold by all four products in each month. "
               f"The trend is going upward. Sales increased from {monthly_total[0]} units in "
               f"January to {monthly_total[-1]} units in June. Markers and value labels are added "
               "on every point so the exact numbers can be read easily.", 3)
    chart_page(pdf, bar_png, "Chart 2: Bar Chart - Product-wise Sales Comparison",
               f"This bar chart compares the total 6-month sales of each product. {top_product} "
               f"is clearly the highest ({product_total[top_product]} units) and {low_product} "
               f"is the lowest ({product_total[low_product]} units). Each product has its own "
               "colour and the value is written on top of the bar.", 4)
    chart_page(pdf, pie_png, "Chart 3: Pie Chart - Contribution of Each Product",
               "The pie chart shows what percentage of the total sales comes from each product. "
               f"Headphones have the biggest slice ({share['Headphones']:.1f}%), followed by "
               f"Smartphones ({share['Smartphones']:.1f}%), Laptops ({share['Laptops']:.1f}%) "
               f"and Smartwatches ({share['Smartwatches']:.1f}%). The biggest slice is pulled "
               "out a little to highlight it.", 5)
    chart_page(pdf, multi_png, "Chart 4: Multiple Line Chart - All Products",
               "This chart puts all four products on the same axes so they can be compared "
               "month by month. Every product has a different colour and marker. Headphones stay "
               "on top the whole time, while the Smartwatches line is rising the fastest.", 6)
    chart_page(pdf, subplot_png, "Chart 5: Subplots - All Charts in One Figure",
               "Here the line chart, bar chart, pie chart and multiple line chart are drawn "
               "together in one 2 x 2 figure using plt.subplots(). This gives a quick overview "
               "of the whole sales data on a single page.", 7)

    # ---------------- Analysis page(s) ----------------
    page = new_page()
    page.text(0.5, 0.94, "Analysis of Sales Results", ha="center", fontsize=16,
              fontweight="bold")
    y = 0.89
    for heading, body in analysis.items():
        page.text(0.09, y, heading, fontsize=12, fontweight="bold", va="top")
        y -= 0.03
        y = write_paragraph(page, body, y, size=10.3, width=90)
        y -= 0.025
    add_page_footer(page, 8)
    pdf.savefig(page)
    plt.close(page)

    info = pdf.infodict()
    info["Title"] = "Python Data Visualization Project Using Matplotlib"
    info["Author"] = "Muhammad Saqlain"

print("PDF report saved:", PDF_PATH)
print("Done!")
