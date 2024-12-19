import matplotlib.pyplot as plt
import os

plt.figure()
plt.plot([1, 2, 3], [4, 5, 6])
plt.title("Test Plot")
plt.tight_layout()

output_dir = '/workspaces/codespaces-jupyter/Reese/Semester 1 Final'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
image_path = os.path.join(output_dir, 'test_plot.png')

try:
    plt.savefig(image_path)
    print(f"Graph saved successfully at: {image_path}")
except Exception as e:
    print(f"Failed to save graph: {e}")
