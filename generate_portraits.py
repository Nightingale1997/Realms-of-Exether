import glob
from pathlib import Path
from os import getcwd, chdir

root_dir = "./"

ASSETS_PATH = "src/output/skins"
ACCESSORIES_PATH = "src/output/accessories"
PATHS_TO_DELETE = [ASSETS_PATH, ACCESSORIES_PATH]


def inPath(flags: list[str], path: str):
    for flag in flags:
        if flag in Path(path).parts:
            return True
    return False


def determineTags(is_slim: bool, empty_override: bool = False):
    if empty_override:
        return ""
    if is_slim:
        return "base_slim"
    else:
        return "base_model"


def check_slim_file_exists(file_path: str) -> bool:
    slim_path = (
        Path(file_path).parent
        / "slim"
        / (Path(file_path).stem + "_slim" + Path(file_path).suffix)
    )
    return slim_path.exists()


def main():
    # Fixes path if it is an executable in dist~
    if getcwd()[-4:] == "dist":
        print("Moving working directory to root of mod folder")
        chdir("..")
    else:
        print(
            "Executable not being run from expected folder, move to dist/ folder if issues arise"
        )

    for pathToDelete in PATHS_TO_DELETE:
        Path(pathToDelete).mkdir(parents=True, exist_ok=True)
        for file in Path(pathToDelete).iterdir():
            file.unlink()

    stored_clothes = {}
    for dds_path in glob.iglob(
        root_dir + "gfx/models/skins/skins_textures/**/*.dds", recursive=True
    ):
        parent_dir = Path(dds_path).parent.parent.name
        is_slim = False
        has_other_version_equivalent = False
        if parent_dir == "slim":
            parent_dir = Path(dds_path).parent.parent.name
            is_slim = True
        else:
            has_other_version_equivalent = check_slim_file_exists(dds_path)
        if parent_dir == "players":
            shader_dir = "body"
        else:
            shader_dir = parent_dir
        relative_path = (
            Path(dds_path).relative_to("gfx/models/skins/skins_textures").as_posix()
        )
        print(relative_path)
        filename = Path(dds_path).stem
        template = f"""pdxmesh = {{
        name = "{filename}_mesh"
        file = "hm_prophet.mesh"
        scale = 1.6
        meshsettings = {{
            name = "prophet_shieldShape"
            index = 0
            texture_diffuse = "skins_textures/{relative_path}"
            shader = "portrait_attachment_alpha_to_coverage"
            shader_file = "gfx/models/skins/{shader_dir}.shader"
        }}
    }}
    entity = {{
        name = "{filename}_entity"
        pdxmesh = "{filename}_mesh"
    }}

    """
        if inPath(["body", "players"], dds_path):
            entity_registration = f"""{filename} = {{
        set_tags = "{determineTags(is_slim)}"
        entity = {{ required_tags = "" shared_pose_entity = head entity = "{filename}_entity" }}
    """
        else:
            entity_registration = f"""{filename} = {{
        entity = {{ required_tags = "{determineTags(is_slim)}" shared_pose_entity = head entity = "{filename}_entity" }}
    """
            if has_other_version_equivalent:
                entity_registration += f"""    entity = {{ required_tags = "base_slim" shared_pose_entity = head entity = "{filename}_slim_entity" }}\n"""
        entity_registration += "}\n\n"

        # Create a new file with the parent directory name
        with open(f"{ASSETS_PATH}/{parent_dir}.asset", "a") as f:
            f.write(template)

        with open(f"{ACCESSORIES_PATH}/{parent_dir}.txt", "a") as f:
            f.write(entity_registration)

if __name__ == "__main__":
    main()
