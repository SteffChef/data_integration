import os
import csv
import pkg_resources

def get_library_sizes():
    libraries = []
    for dist in pkg_resources.working_set:
        lib_name = dist.project_name
        try:
            lib_path = os.path.join(dist.location, lib_name.replace("-", "_"))  # Normalize name
            if os.path.exists(lib_path):
                lib_size = sum(
                    os.path.getsize(os.path.join(dirpath, f))
                    for dirpath, _, filenames in os.walk(lib_path)
                    for f in filenames
                )
                libraries.append((lib_name, lib_size / (1024 * 1024)))  # Convert to MB
            else:
                libraries.append((lib_name, 0.0))  # Library folder not found
        except Exception as e:
            libraries.append((lib_name, f"Error: {str(e)}"))
    return libraries

def export_to_csv(sizes, filename="library_sizes.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Library", "Size (MB)"])
        writer.writerows(sizes)

sizes = get_library_sizes()
export_to_csv(sizes)
print("Library sizes exported to library_sizes.csv")
