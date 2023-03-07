import os 
from interactions import Client

def extensions(client: Client, directory: str):
    cogs = [
        module[:-3]
        for module in os.listdir(f"./{directory}")
        if module not in "__init__.py" and module[-3:] == ".py"
    ]

    if cogs or cogs == []:
        print("Importing extensions:", len(cogs), ", ".join(cogs))
    else:
        print("Could not import any extensions!")

    for cog in cogs:
        try:
            client.load(f"cogs.{cog}")
        except Exception:  # noqa
            print(f"Could not load a {directory} extension: {cog}", exc_info=True)