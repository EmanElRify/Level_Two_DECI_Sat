path = input("Enter the path: ")
if "#" in path:
    path = path.replace("#", "%23")
if " " in path:
    path = path.replace(" ", "%20")
print(path)