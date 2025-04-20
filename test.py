# Synchronous usage
from gitingest import ingest

summary, tree, content = ingest("https://github.com/NevroHelios/automated-data-analysis")

print("Summary:", summary)
print("Tree:", tree)
print("Content:", content)


with open("summary.txt", "w") as f:
    f.write(summary)
with open("tree.txt", "w", encoding="utf-8") as f:
    f.write(tree)
with open("content.txt", "w") as f:
    f.write(content)