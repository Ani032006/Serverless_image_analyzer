import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_fig2(output_path="submissions/sequential_flowchart.jpg"):
    # Clean, perfectly centered 2-column layout matching ASCII diagram
    fig, ax = plt.subplots(figsize=(11, 9.5), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 9.5)
    ax.axis('off')

    def draw_box(x, y, w, h, title, subtitle="", is_dlq=False):
        linestyle = '--' if is_dlq else '-'
        rect = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.08,rounding_size=0.15",
            edgecolor="black",
            facecolor="#FFFFFF",
            linewidth=1.8,
            linestyle=linestyle
        )
        ax.add_patch(rect)
        
        if subtitle:
            ax.text(x + w/2, y + h*0.62, title,
                    ha='center', va='center', fontsize=10.5, fontweight='bold', color='black', family='sans-serif')
            ax.text(x + w/2, y + h*0.32, subtitle,
                    ha='center', va='center', fontsize=9, fontweight='normal', color='#222222', family='sans-serif')
        else:
            ax.text(x + w/2, y + h*0.5, title,
                    ha='center', va='center', fontsize=10.5, fontweight='bold', color='black', family='sans-serif')

    def draw_diamond(cx, cy, w, h, title):
        pts = [
            [cx, cy + h/2],
            [cx + w/2, cy],
            [cx, cy - h/2],
            [cx - w/2, cy]
        ]
        poly = patches.Polygon(pts, closed=True, edgecolor='black', facecolor='#FFFFFF', linewidth=1.8)
        ax.add_patch(poly)
        ax.text(cx, cy, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='black', family='sans-serif')

    def draw_arrow(x1, y1, x2, y2, label="", label_pos=(0.5, 0.5), label_align=('center', 'bottom')):
        arrow = patches.FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle='-|>,head_length=6,head_width=4',
            color='black',
            linewidth=1.6
        )
        ax.add_patch(arrow)
        if label:
            lx = x1 + (x2 - x1) * label_pos[0]
            ly = y1 + (y2 - y1) * label_pos[1]
            ax.text(lx, ly, label,
                    ha=label_align[0], va=label_align[1],
                    fontsize=8.5, fontweight='bold', color='black', family='sans-serif',
                    bbox=dict(boxstyle="square,pad=0.2", fc="white", ec="none"))

    # Central Column Alignment:
    # Center X = 5.5
    # Left Column Center = 2.6  (Box width 3.0 -> [1.1, 4.1])
    # Right Column Center = 8.4 (Box width 3.0 -> [6.9, 9.9])

    # 1. User Upload (Top Left)
    draw_box(0.6, 7.8, 2.5, 1.1, "User Upload")

    # 2. Amazon S3 (Top Center)
    draw_box(4.0, 7.8, 3.0, 1.1, "Amazon S3", "incoming/")
    draw_arrow(3.1, 8.35, 4.0, 8.35)

    # 3. AWS Lambda (Center)
    draw_box(4.0, 6.0, 3.0, 1.1, "AWS Lambda", "handler.py")
    draw_arrow(5.5, 7.8, 5.5, 7.1, label="(s3:ObjectCreated)", label_pos=(0.5, 0.5), label_align=('left', 'center'))

    # 4. Decision Diamond (Directly under Lambda, centered at x=5.5, y=4.4)
    draw_diamond(5.5, 4.4, 3.0, 1.2, "Extension\nSupported?")
    draw_arrow(5.5, 6.0, 5.5, 5.0)

    # 5. Left Branch: [YES] -> Rekognition API (centered at x=2.6)
    # Horizontal line from diamond left (x=4.0) to x=2.6, then down to y=3.4
    ax.plot([4.0, 2.6, 2.6], [4.4, 4.4, 3.45], color='black', linewidth=1.6)
    arrow_yes = patches.FancyArrowPatch(
        (2.6, 3.45), (2.6, 3.4),
        arrowstyle='-|>,head_length=6,head_width=4',
        color='black',
        linewidth=1.6
    )
    ax.add_patch(arrow_yes)
    ax.text(2.6, 4.6, "Yes", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='black',
            bbox=dict(boxstyle="square,pad=0.2", fc="white", ec="none"))

    draw_box(1.1, 2.3, 3.0, 1.1, "Rekognition API", "detect_labels()")

    # 6. Right Branch: No -> SQS DLQ (centered at x=8.4)
    # Horizontal line from diamond right (x=7.0) to x=8.4, then down to y=3.4
    ax.plot([7.0, 8.4, 8.4], [4.4, 4.4, 3.45], color='black', linewidth=1.6)
    arrow_no = patches.FancyArrowPatch(
        (8.4, 3.45), (8.4, 3.4),
        arrowstyle='-|>,head_length=6,head_width=4',
        color='black',
        linewidth=1.6
    )
    ax.add_patch(arrow_no)
    ax.text(8.4, 4.6, "No", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='black',
            bbox=dict(boxstyle="square,pad=0.2", fc="white", ec="none"))

    draw_box(6.9, 2.3, 3.0, 1.1, "SQS DLQ", "ImageProcessingDLQ", is_dlq=True)
    ax.text(8.4, 1.9, "(UNSUPPORTED_FORMAT event)", ha='center', va='top', fontsize=8.5, style='italic', color='#444444')

    # 7. Bottom Left: DynamoDB (centered at x=2.6)
    draw_box(1.1, 0.5, 3.0, 1.1, "DynamoDB", "Table: ImageTags")
    draw_arrow(2.6, 2.3, 2.6, 1.6, label="(Label Payload)", label_pos=(0.5, 0.5), label_align=('left', 'center'))

    # 8. Bottom Right: CloudWatch Logs (centered at x=8.4)
    draw_box(6.9, 0.5, 3.0, 1.1, "CloudWatch Logs", "(Structured JSON)")
    
    # Arrow DynamoDB -> CloudWatch Logs
    draw_arrow(4.1, 1.05, 6.9, 1.05, label="Audit Trail", label_pos=(0.5, 0.5), label_align=('center', 'bottom'))

    # Caption
    plt.figtext(0.5, 0.015,
                "Fig. 2: Sequential execution pipeline and error diversion branch.",
                ha="center", fontsize=9.5, fontweight="roman", style="italic", family="serif")

    plt.tight_layout()
    plt.savefig(output_path, format="jpg", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Fig. 2 successfully saved to {output_path}")

if __name__ == "__main__":
    generate_fig2()
