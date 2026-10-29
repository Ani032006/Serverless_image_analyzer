import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_diagram(output_path="submissions/architecture_diagram.jpg"):
    # Set up figure with high DPI and clean white background
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    # Box styling helper
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
                    ha='center', va='center', fontsize=11, fontweight='bold', color='black', family='sans-serif')
            ax.text(x + w/2, y + h*0.32, subtitle,
                    ha='center', va='center', fontsize=9.5, fontweight='normal', color='#222222', family='sans-serif')
        else:
            ax.text(x + w/2, y + h*0.5, title,
                    ha='center', va='center', fontsize=11, fontweight='bold', color='black', family='sans-serif')

    # Arrow helper
    def draw_arrow(x1, y1, x2, y2, label="", label_pos=(0.5, 0.5), label_align=('center', 'bottom'), rad=0.0):
        connectionstyle = f"arc3,rad={rad}" if rad != 0.0 else "arc3,rad=0"
        arrow = patches.FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle='-|>,head_length=7,head_width=4.5',
            connectionstyle=connectionstyle,
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
                    bbox=dict(boxstyle="square,pad=0.25", fc="white", ec="none"))

    # Boxes:
    # 1. Amazon S3 (Top Left)
    draw_box(0.6, 5.4, 2.7, 1.3, "Amazon S3", "(incoming/*)")

    # 2. AWS Lambda (Top Right)
    draw_box(5.8, 5.4, 3.4, 1.3, "AWS Lambda", "handler.py (Python 3.12)")

    # Arrow: S3 -> Lambda
    draw_arrow(3.3, 6.05, 5.8, 6.05, label="S3:ObjectCreated\n(Event Notification)", label_pos=(0.5, 0.5), label_align=('center', 'bottom'))

    # Middle Row:
    # 3. Amazon Rekognition (Middle Left)
    draw_box(3.8, 2.9, 2.8, 1.3, "Amazon Rekognition", "DetectLabels API")

    # 4. Amazon SQS DLQ (Middle Right)
    draw_box(7.4, 2.9, 2.8, 1.3, "Amazon SQS DLQ", "ImageProcessingDLQ", is_dlq=True)

    # Arrow: Lambda -> Rekognition (Valid Image)
    draw_arrow(6.6, 5.4, 5.2, 4.2, label="Valid Image\n(.jpg, .jpeg, .png)", label_pos=(0.4, 0.5), label_align=('right', 'center'))

    # Arrow: Lambda -> SQS DLQ (Invalid/Error)
    draw_arrow(8.1, 5.4, 8.1, 4.2, label="Invalid / Error\n(send_to_dlq)", label_pos=(0.5, 0.5), label_align=('left', 'center'))

    # Bottom Row:
    # 5. Amazon DynamoDB (Bottom Left)
    draw_box(3.8, 0.6, 2.8, 1.3, "Amazon DynamoDB", "Table: ImageTags")

    # 6. CloudWatch Logs (Bottom Right)
    draw_box(7.4, 0.6, 2.8, 1.3, "CloudWatch Logs", "(Structured JSON)")

    # Arrow: Rekognition -> DynamoDB
    draw_arrow(5.2, 2.9, 5.2, 1.9, label="Extracted Labels\n& Confidence", label_pos=(0.5, 0.5), label_align=('left', 'center'))

    # Arrow: Lambda -> CloudWatch Logs (clean wide loop clear of DLQ)
    draw_arrow(9.2, 5.8, 10.2, 1.25, label="Execution\nTelemetry", label_pos=(0.55, 0.5), label_align=('left', 'center'), rad=-0.35)

    # Caption (IEEE Standard)
    plt.figtext(0.5, 0.02,
                "Fig. 1: Architecture of the Event-Driven Serverless AI Image Tagging and Analysis Pipeline with SQS DLQ.",
                ha="center", fontsize=9.5, fontweight="roman", style="italic", family="serif")

    plt.tight_layout()
    plt.savefig(output_path, format="jpg", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Diagram successfully saved to {output_path}")

if __name__ == "__main__":
    generate_diagram()
