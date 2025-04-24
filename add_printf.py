import os.path
import re
import xml.etree.ElementTree as ET

# ----------------------------- Color definitions ---------------------------- #


def prRed(skk): return f"\033[91m{skk}\033[00m"
def prGreen(skk): return f"\033[92m{skk}\033[00m"
def prYellow(skk): return f"\033[93m{skk}\033[00m"
def prLightPurple(skk): return f"\033[94m{skk}\033[00m"
def prPurple(skk): return f"\033[95m{skk}\033[00m"
def prCyan(skk): return f"\033[96m{skk}\033[00m"
def prLightGray(skk): return f"\033[97m{skk}\033[00m"
def prBlack(skk): return f"\033[98m{skk}\033[00m"

# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
H_LINE = prCyan(
    "# ---------------------------------------------------------------------------- #\n"
)

SCRIPT_TITLE = (
    H_LINE
    + prCyan(
        "#             FIUBA - Taller de sistemas embebidos - 1C 2025                   #\n"
    )
    + H_LINE
)

AUTHORS = prPurple(
    "\
\n\
                    Guido Rodriguez - Karla Duque\n\
             guerodriguez@fi.uba.ar - kduque@fi.uba.ar\n\
\n"
)

SCRIPT_CAPTION = prLightGray(
    "\
Este script se encarga de agregar las configuraciones necesarias para\n\
utilizar el printf en VSCode en un esquema semihosting mediante OpenOCD\n\
\n"
)

ADD_KEYWORD = prGreen("Agrega")
CONFIG_KEYWORD = prYellow("Configura")
OPTIONAL = prLightPurple("(Opcional)")

SCRIPT_DESCRIPTION = (
    f"\
    - {ADD_KEYWORD} librerias como rdimon y sus configuraciones\n\
    - {ADD_KEYWORD} opciones de linking para utilizar en modo semihosting\n\
    - {ADD_KEYWORD} una task para en VSCode debug mediante OpenOCD\n\
    - {CONFIG_KEYWORD} el servidor OpenOCD en modo semihosting\n\
    - {OPTIONAL} {ADD_KEYWORD} una serie de botones en la status bar \n\
                para facilitar el desarrollo\n"
    + H_LINE
)
# ---------------------------------------------------------------------------- #

# ----------------------------- Welcome messagge ----------------------------- #


def welcome_msg():
    print(SCRIPT_TITLE + AUTHORS + SCRIPT_CAPTION + SCRIPT_DESCRIPTION)


# ---------------------------------------------------------------------------- #

# -------------------------- Not first run messagge -------------------------- #


def not_first_run_msg():
    SCRIPT_CAPTION_WARNING = (
        prRed(
            f"\
    Se detecto que este script fue ejecutado previamente y volver a hacerlo sin\n\
    revertir los cambios efectuados puede generar errores o conflictos en la\n\
    configuracion. Si realmente queres volver a ejecutarlo elimina el archivo \n\
    {prLightPurple(FIRST_RUN_FILE_PATH)}\n\n"
        )
        + prRed("    Y reverti los cambios efectuados el los sigientes archivos:\n")
        + prLightPurple("\t./.vscode/launch.json\n")
        + prLightPurple("\t./cmake/stm32cubemx/CMakeLists.txt\n")
        + prLightPurple("\t./cmake/gcc-arm-none-eabi.cmake\n")
    )

    print(SCRIPT_TITLE + AUTHORS + SCRIPT_CAPTION_WARNING + H_LINE)


# ---------------------------------------------------------------------------- #


# ------------------------------- Dry run check ------------------------------ #
FIRST_RUN_FILE_PATH = "add_printf_dry_run.bin"


def is_script_first_run():

    if os.path.exists(FIRST_RUN_FILE_PATH):
        return False

    with open(FIRST_RUN_FILE_PATH, "wb") as f:
        f.write(b"first_run_complete")
        f.close()
    return True


# ---------------------------------------------------------------------------- #


# -------------------------- Compiler linker options ------------------------- #
GCC_ARM_NONE_EABI_LINKER_OPTIONS = '\n\
# ---------------------------------------------------------------------------- #\n\
# Configuracion printf en semihosting\n\
# ---------------------------------------------------------------------------- #\n\
# Incluimos la biblioteca rdimon que le indica que podemos usar las systemcalls\n\
# pero estas son manejadas por el debugger controlado por el HOST\n\
set(CMAKE_C_LINK_FLAGS \"${CMAKE_C_LINK_FLAGS} -lrdimon\")\n\
set(CMAKE_C_LINK_FLAGS \"${CMAKE_C_LINK_FLAGS} -specs=rdimon.specs\")\n\
# Excluimos las llamadas del sistema (evitamos redefinir funciones basicas\n\
# como _write, _read, _open, _kill, _etc) y prevenimos posibles errores de \n\
# uso de las syscalls por parte del TARGET\n\
set(CMAKE_C_LINK_FLAGS \"${CMAKE_C_LINK_FLAGS} --specs=nosys.specs\")\n\
# ---------------------------------------------------------------------------- #\n\
'
PATH_GCC_ARM_COMPILER = "cmake/gcc-arm-none-eabi.cmake"


def add_linking_options(options):
    file_gcc_arm_compiler = open(PATH_GCC_ARM_COMPILER, "a")
    file_gcc_arm_compiler.write(options)
    file_gcc_arm_compiler.close()


# ---------------------------------------------------------------------------- #


# --------------------------- Exclude syscalls file -------------------------- #
PATH_CMAKE_LIST_CUBEMX = "cmake/stm32cubemx/CMakeLists.txt"


def remove_syscall_link():
    file_cmake_list_cubemx = open(PATH_CMAKE_LIST_CUBEMX, "r")
    dump_cmake_list = file_cmake_list_cubemx.readlines()
    file_cmake_list_cubemx.close()

    file_cmake_list_cubemx = open(PATH_CMAKE_LIST_CUBEMX, "w")
    for line in dump_cmake_list:
        if line.find("syscalls.c") != -1 and line.find("#") == -1:
            file_cmake_list_cubemx.write("#" + line)
        else:
            file_cmake_list_cubemx.write(line)
    file_cmake_list_cubemx.close()


# ---------------------------------------------------------------------------- #


# ------------------------- Semihosting config server ------------------------ #
SEMIHOSTING_CONFIG = """\
        // --------------------------------------------------------------------------\n\
        // Configuracion semihosting - printf \n\
        // --------------------------------------------------------------------------\n\
        {{\n\
            \"name\": \"Debug con OpenOCD\",\n\
            \"cwd\": \"${{workspaceFolder}}\",\n\
            \"type\": \"cortex-debug\",\n\
            \"executable\": \"${{command:cmake.launchTargetPath}}\",\n\
            \"request\": \"launch\",\n\
            \"servertype\": \"openocd\",\n\
            \"serverpath\": "{_server_path}",\n\
            \"configFiles\": [\n\
                "{_debug_cfg_file}"\n\
            ],\n\
            \"serverArgs\": [\n\
                \"-s\",\n\
                "{_scripts}",\n\
                // \"-d3\"\n\
            ],\n\
            \"device\":"{_target}",\n\
            \"svdFile\": \"${{config:STM32VSCodeExtension.cubeCLT.path}}/STMicroelectronics_CMSIS_SVD/{_target_svd}\",\n\
            \"runToEntryPoint\": \"main\",\n\
            \"showDevDebugOutput\": \"raw\",\n\
            \"preLaunchCommands\": [\n\
                \"monitor arm semihosting enable\",\n\
                \"monitor sleep 100\",\n\
            ]\n\
        }},\n\
        // --------------------------------------------------------------------------\n\
        """
# ---------------------------------------------------------------------------- #

# --------------------------- Config OpenOCD server -------------------------- #
PATH_LAUNCH_JSON = ".vscode/launch.json"


def set_openocd_vscode_task(
    open_ocd_server_path,
    target_mcu_name,
    target_mcu_svd_filename,
    open_ocd_debug_cfg_path,
    open_ocd_scripts_path,
):

    file_launch_json = open(PATH_LAUNCH_JSON, encoding="utf-8 ", mode="r")
    dump_json = file_launch_json.readlines()
    file_launch_json.close()

    was_added_configuration = False

    file_launch_json = open(PATH_LAUNCH_JSON, encoding="utf-8", mode="w")

    for line in dump_json:
        if line.find("configurations") != -1 and not was_added_configuration:

            actual_line = line
            actual_index = dump_json.index(line)

            while actual_line.find("[") == -1 or actual_line[0] == "\n":
                actual_line = dump_json[actual_index + 1]
                actual_index += 1

            actual_line += "\n" + SEMIHOSTING_CONFIG.format(
                _server_path=open_ocd_server_path,
                _target=target_mcu_name,
                _debug_cfg_file=open_ocd_debug_cfg_path,
                _scripts=open_ocd_scripts_path,
                _target_svd=target_mcu_svd_filename,
            )

            line = actual_line
            was_added_configuration = True

        file_launch_json.write(line)

    file_launch_json.close()


# ---------------------------------------------------------------------------- #

# ----------------------------- Parse config data ---------------------------- #


def parse_config_file(file_path):
    config = {}

    # Expresión regular para detectar claves y valores
    # TODO - REVISAR SI SIRVE PARA WIN
    pattern = re.compile(r"^\s*([\w\-]+)\s*=\s*(.*?)\s*$")

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = pattern.match(line)
            if match:
                key, value = match.groups()
                # Si no hay valor, deja None
                config[key] = value.strip() if value else None

    return config


# ---------------------------------------------------------------------------- #

# ----------------------------- Wait until accept ---------------------------- #


def wait_until_accept():

    print(
        prYellow(">>> [INFO]  ")
        + " -\tCuando termines de configurar los datos presiona "
        + "[Y/y/Enter] sino [N/n] para cancelar"
    )

    while True:
        respuesta = (
            input(
                prCyan("<<< [INPUT]  ")
                + "-\t"
                + "¿Terminaste la configuración? [Y/N]: "
            )
            .strip()
            .lower()
        )

        if respuesta in ["y", ""]:
            print("")
            # print(prYellow(">>> [INFO]    ") + " - Continuando con el proceso...\n")
            break
        elif respuesta == "n":
            print("")
            print(prRed(">>> [CANCEL]") +
                  " - Operación cancelada por el usuario")
            print(
                prYellow(">>> [INFO]")
                + f" - Para correr de nuevo el script por favor eliminar el archivo {FIRST_RUN_FILE_PATH}"
            )
            exit(1)
        else:
            print(
                prYellow(">>> [WARN]  ")
                + " -\tEntrada no válida. Por favor, ingresa 'Y' para continuar o 'N' para cancelar"
            )


# ---------------------------------------------------------------------------- #


def wait_for_custom_choice(options, cancel_option):
    # print(prYellow(">>> [INFO]  ") + " - Selecciona una opción:")

    for key, description in options.items():
        print(prGreen(f"\t\t({key})") + f" - {description}")

    while True:
        selected_option = input(
            prCyan("<<< [INPUT]  ") + "-\tSelecciona una opción: "
        ).strip()

        if selected_option in options:
            print("")
            print(
                prYellow(">>> [INFO]  ") +
                f" -\tElegiste: {options[selected_option]}\n"
            )
            return selected_option
        elif selected_option == cancel_option:
            print("")
            print(prRed(">>> [CANCEL]") +
                  " - Operación cancelada por el usuario.")
            print(
                prYellow(">>> [INFO]")
                + f" - Para correr de nuevo el script por favor eliminar el archivo {FIRST_RUN_FILE_PATH}"
            )
            exit(1)
        else:
            print(
                prYellow(">>> [WARN]  ")
                + " -\tEntrada no válida. Ingresa una de las opciones disponibles\n"
            )


# ---------------------------------------------------------------------------- #


# -------------------------- Semihosting data input -------------------------- #
SEMIHOSTING_DATA_FILE_TEMPLATE = "\
# Agrega la ruta al servidor de OpenOCD de ST\n\
# Si realizaste una instalacion por defecto \n\
# este se encuentra habitualmente en:\n\
# [LINUX]: /home/TU_USUARIO/st/stm32cubeide_VERSION/plugins/com.st.stm32cube.ide.mcu.externaltools.openocd.linux64_NUMEROS_DE_VERSION/tools/bin/openocd\n\
# [LINUX_ALTERNATIVA]: /opt/st/stm32cubeide_VERSION/plugins/com.st.stm32cube.ide.mcu.externaltools.openocd.linux64_NUMEROS_DE_VERSION/tools/bin/openocd\n\
# [WIN]: C:\\st\\stm32cubeide_VERSION\\plugins\\com.st.stm32cube.ide.mcu.externaltools.openocd.linux64_NUMEROS_DE_VERSION\\tools\\bin\\openocd.exe\n\
path_to_OpenOCD = \n\
\n\
# Agrega la ruta a la carpeta de scripts de OpenOCD de ST\n\
# Si realizaste una instalacion por defecto \n\
# esta se encuentra habitualmente en:\n\
# [LINUX]: /home/TU_USUARIO/st/stm32cubeide_VERSION/plugins/com.st.stm32cube.ide.mcu.debug.openocd_NUMEROS_DE_VERSION/resources/openocd/st_scripts\n\
# [LINUX ALTERNATIVA]: /opt/st/stm32cubeide_VERSION/plugins/com.st.stm32cube.ide.mcu.debug.openocd_NUMEROS_DE_VERSION/resources/openocd/st_scripts\n\
# [WIN]: C:\\st\\stm32cubeide_VERSION\\plugins\\com.st.stm32cube.ide.mcu.debug.openocd_NUMEROS_DE_VERSION\\resources\\openocd\\st_scripts\n\
path_to_OpenOCD_scripts = \n\
\n\
# Agrega el nombre asociado a tu microcontrolador (EJ: STM32F103RBTx)\n\
# - Abri CubeMX con tu proyecto y en la pestaña 'Project Manager' busca 'MCU Reference'\n\
# - Copia y pega ese valor \n\
mcu_reference =\n\
\n\
# Agrega el nombre del archivo de descripcion SVD de tu Target (NO LA RUTA. EJ: STM32F103.svd)\n\
# Si realizaste una instalacion por defecto \n\
# esta se encuentra habitualmente en:\n\
# [LINUX]: /opt/st/stm32cubeclt_VERSION/STMicroelectronics_CMSIS_SVD/ACA_VA_EL_NOMBRE_DEL_DEVICE\n\
# [LINUX_ALTERNATIVA]: /home/TU_USUARIO/st/stm32cubeclt_VERSION/STMicroelectronics_CMSIS_SVD/ACA_VA_EL_NOMBRE_DEL_DEVICE\n\
# [WIN]: C:\\st\\stm32cubeclt_VERSION/STMicroelectronics_CMSIS_SVD/ACA_VA_EL_NOMBRE_DEL_DEVICE\n\
mcu_target_svd =\n\
"
# ---------------------------------------------------------------------------- #

# ------------------------ OpenOCD debug file default ------------------------ #
OPEN_OCD_DEBUG_CONFIG_TEMPLATE = """
# This is an NUCLEO-F103RB board with a single STM32F103RBTx chip
#
# Generated by STM32CubeIDE
# Take care that such file, as generated, may be overridden without any early notice. Please have a look to debug launch configuration setup(s)
source [find interface/stlink-dap.cfg]

set WORKAREASIZE 0x5000

transport select "dapdirect_swd"

set CHIPNAME STM32F103RBTx
set BOARDNAME NUCLEO-F103RB

# Enable debug when in low power modes
set ENABLE_LOW_POWER 1

# Stop Watchdog counters when halt
set STOP_WATCHDOG 1

# STlink Debug clock frequency
set CLOCK_FREQ 8000

# Reset configuration
# use software system reset if reset done
reset_config none
set CONNECT_UNDER_RESET 0
set CORE_RESET 0

# ACCESS PORT NUMBER
set AP_NUM 0
# GDB PORT
set GDB_PORT 3333

# BCTM CPU variables
source [find target/stm32f1x.cfg]
"""
# ---------------------------------------------------------------------------- #

# ---------------------------- Semihosting config ---------------------------- #
FILE_IS_EMPTY = 0


def wait_until_data_is_valid(file_path, err_msg, callback=None, validate_fields=False):

    file_is_not_valid = True
    while file_is_not_valid:

        wait_until_accept()

        with open(file_path, "r") as f:
            if len(f.read()) == FILE_IS_EMPTY:
                print(prRed(">>> [ERROR] ") + " - \t" + err_msg)
            else:
                file_is_not_valid = False
            f.close()

        if validate_fields:
            if callback(file_path):
                file_is_not_valid = True
                print(prRed(">>> [ERROR] ") + " - \t" + err_msg)
            else:
                file_is_not_valid = False


def semihosting_parser(file_path):
    semihosting_dict = parse_config_file(file_path)
    return None in semihosting_dict.values()


def get_cubeide_path():

    print(
        prYellow(">>> [INFO]  ")
        + " -\tPara continuar"
        + prPurple(" ES NECESARIO ")
        + "que tengas instalado CubeIDE y \n"
        + "\t\tselecciones si queres que el script busque los archivos\n"
        + "\t\tnecesarios en la ruta de instalación por defecto de \n"
        + "\t\tSTM32CubeIDE o en una ruta personalizada"
    )

    OPTION_CUBEIDE_DEFAULT_PATH = "1"
    OPTION_CUBEIDE_CUSTOM_PATH = "2"
    OPTION_ABORT = "3"

    options_cubeide_message = {
        OPTION_CUBEIDE_DEFAULT_PATH: "Dejar que el script busque en las rutas habituales",
        OPTION_CUBEIDE_CUSTOM_PATH: "Buscar en una ruta personalizada",
    }

    option = wait_for_custom_choice(options_cubeide_message, OPTION_ABORT)

    if option == OPTION_CUBEIDE_DEFAULT_PATH:
        cube_ide_path = get_lastest_cube_ide_path()
    elif option == OPTION_CUBEIDE_CUSTOM_PATH:
        cube_ide_path = get_user_custom_cubeide_path()

    if cube_ide_path == ERR_PATH_NOT_FOUND and option == OPTION_CUBEIDE_DEFAULT_PATH:
        print(prRed(">>> [ERROR] ") +
              " - \tNo se encontro CubeIDE en la ruta predeterminada\n")
        exit(1)
    elif cube_ide_path == ERR_CUBE_IDE_NOT_FOUND and option == OPTION_CUBEIDE_CUSTOM_PATH:
        print(prRed(">>> [ERROR] ") +
              " - \tNo se encontro CubeIDE en la ruta personalizada\n")
        exit(1)

    print(
        prYellow(">>> [INFO]  ")
        + " -\tSe encontro la version mas reciente en:\n"
        + f"\t\t{prYellow(cube_ide_path)}\n"
    )

    return cube_ide_path

# ---------------------------------------------------------------------------- #


def get_valid_input(prompt_message, input_message, validation_function):
    print(prLightPurple(prompt_message + "\n"))

    while True:
        user_input = input(prCyan("<<< [INPUT]  ") + f"-\t{input_message}")
        if validation_function(user_input):
            return user_input


def validate_cubeide_path(cubeide_path):
    retval = find_cube_ide_path([cubeide_path])
    if retval == ERR_CUBE_IDE_NOT_FOUND:
        print(
            prRed(">>> [ERROR] ") +
            f" - \tNo se encontro CubeIDE en {cubeide_path}\n"
        )
    elif retval == ERR_PATH_NOT_FOUND:
        print(prRed(">>> [ERROR] ") +
              " - \tRuta no encontrada, volve a intentarlo\n")
    return not (retval == ERR_CUBE_IDE_NOT_FOUND or retval == ERR_PATH_NOT_FOUND)


def get_user_custom_cubeide_path():
    return find_cube_ide_path(
        [
            get_valid_input(
                prompt_message="Ingresar la ruta donde instalaste STM32CubeIDE",
                input_message="Ruta personalizada: ",
                validation_function=validate_cubeide_path,
            )
        ]
    )


# ------------------------------ OpenOCD config ------------------------------ #


def print_help_openocd_debug_cfg():
    print(
        f"""\
    {prLightPurple("Pasos para generar un archivo de configuración de OpenOCD:")}

    1. Crea un proyecto en STM32CubeIDE para el mismo dispositivo o placa.plugins/com.st.stm32cube.ide.mcu.debug.openocd_NUMEROS_DE_VERSION
    2. Abre la configuración de debug. Run => Debug Configurations => STM32 C/C++ Application => Debugger
    3. Cambia la opción de "Debug Probe" de [ST-Link GDB-Server] a [ST-Link OpenOCD].
    4. Configuration Script => Show Generator Options => Mode Setup => Reset Mode => [Software System Reset]
    4. Una vez cambiado y luego de tocar "Apply", STM32CubeIDE generará automáticamente un nuevo archivo en el explorador de proyectos.
    5. Busca el archivo generado en la carpeta de depuración. Su nombre suele ser "<NOMBRE_DEL_PROYECTO> Debug.cfg".
    6. Copia el contenido de este archivo y pégalo en un nuevo archivo de configuración.

    Este archivo se utilizará para configurar OpenOCD correctamente con el dispositivo.
    """
    )


PATH_OPENOCD_DEBUG_FILE = "./OpenOCD_Debug.cfg"


def generate_openocd_debug_file(use_default_content=False):
    with open(PATH_OPENOCD_DEBUG_FILE, "w") as f:
        if use_default_content:
            f.write(OPEN_OCD_DEBUG_CONFIG_TEMPLATE)
        f.close()
    print(
        prGreen(">>> [ADD]   ")
        + " - Se genero el archivo de configuracion del servidor OpenOCD "
        + prPurple("(Ahora completalo)")
        if not use_default_content
        else ""
    )


def set_custom_debug_config_file():
    print(
        prYellow(">>> [INFO]  ")
        + " - Para continuar"
        + prPurple(" ES NECESARIO ")
        + f"que configures el archivo de debug del servidor \n\
               de OpenOCD el archivo que vas a encontrar en {PATH_OPENOCD_DEBUG_FILE}"
    )

    generate_openocd_debug_file()
    print_help_openocd_debug_cfg()

    ERR_MSG_DEBUB_FILE = "El archivo de configuracion de OpenOCD esta vacio y es necesario que sea completado por el usuario"
    wait_until_data_is_valid(
        PATH_OPENOCD_DEBUG_FILE, ERR_MSG_DEBUB_FILE, ERR_MSG_DEBUB_FILE
    )


def get_openocd_server_config():

    print(
        prYellow(">>> [INFO]  ")
        + " -\tPara continuar"
        + prPurple(" ES NECESARIO ")
        + "que elijas si queres configurar un archivo\n"
        + "\t\tde debug del servidor de OpenOCD o utilizar una configuracion por defecto\n"
        + "\t\tbasada en la "
        + prLightPurple("Nucleo-F103")
        + " (que no funcionaria si usas otra placa)"
    )

    OPTION_DEBUG_CFG_DEFAULT = "1"
    OPTION_DEBUG_CFG_CUSTOM = "2"
    OPTION_DEBUG_CFG_ABORT = "3"

    options_debug_cfg = {
        OPTION_DEBUG_CFG_DEFAULT: "Utilizar configuración predeterminada",
        OPTION_DEBUG_CFG_CUSTOM: "Utilizar configuración personalizada",
    }
    option = wait_for_custom_choice(options_debug_cfg, OPTION_DEBUG_CFG_ABORT)

    if option == OPTION_DEBUG_CFG_DEFAULT:
        generate_openocd_debug_file(use_default_content=True)

    # Parsear OpenOCD_debug.cfg
    # - Si validamos si el archivo esta vacio -> ERROR
    elif option == OPTION_DEBUG_CFG_CUSTOM:
        set_custom_debug_config_file()
    # else:
    #     # Salida de programa

    return PATH_OPENOCD_DEBUG_FILE


# ---------------------------------------------------------------------------- #


def normalize_path(path):
    normalized_path = os.path.normpath(path)
    if os.name == "nt":
        return normalized_path.replace("\\", "\\\\").replace("\\\\\\\\", "\\\\")
    else:
        return normalized_path.replace("\\", "/").replace("//", "/")


def get_lastest_cube_ide_path() -> str:

    # Buscamos si existe CubeIDE en alguna de estas rutas:
    # - /home/TU_USUARIO/st/stm32cubeide_VERSION
    # - /opt/st/stm32cubeide_VERSION/
    # - Si estoy en WIN
    #   - C:\\st\\stm32cubeide_VERSION
    # Si hay varias opciones las ordenamos lexicograficamente y tomamos la mayor, es decir la mas actual
    # - En la mas actual buscamos
    #   - plugins/com.st.stm32cube.ide.mcu.debug.openocd_NUMEROS_DE_VERSION/resources/openocd/st_scripts
    #   - plugins/com.st.stm32cube.ide.mcu.externaltools.openocd.linux64_NUMEROS_DE_VERSION/tools/bin/openocd
    #     - Si estoy en WIN agrego .exe a openocd

    USERNAME = os.getlogin()

    if os.name == "posix":
        CUBE_IDE_DIRS = ["/opt/st", f"/home/{USERNAME}/st"]
    else:
        CUBE_IDE_DIRS = ["C:\\st"]

    return find_cube_ide_path(CUBE_IDE_DIRS)


ERR_PATH_NOT_FOUND = -1
ERR_CUBE_IDE_NOT_FOUND = -2


def find_cube_ide_path(paths_to_find: list):
    cube_ide_paths = []
    for cube_dir in paths_to_find:
        try:
            for candidate_dir in os.listdir(cube_dir):
                if "stm32cubeide" in candidate_dir:
                    cube_ide_paths.append(
                        normalize_path(cube_dir + "/" + candidate_dir)
                    )
        except FileNotFoundError:
            # No se encontro en la ruta candidate_dir, buscando en la siguiente
            print(
                prRed(">>> [ERROR] ") +
                f" - \tNo se encontro la ruta {cube_dir}\n"
                + prYellow(">>> [INFO]  ") +
                " - \tBuscando en la siguiente ruta...\n"
            )

    if len(cube_ide_paths) == 0:
        # print(prRed(">>> [ERROR] ") +
        #       f" - \tNo se encontro CubeIDE en {paths_to_find}")
        return ERR_CUBE_IDE_NOT_FOUND

    # Ordeno con la mas reciente al principio
    cube_ide_paths.sort(reverse=True)
    return cube_ide_paths[0]


def get_openocd(cubeide_path):
    plugins_paths = os.listdir(cubeide_path + "/plugins")
    openocd_path = []
    openocd_scripts_path = []

    openocd_name = f"{'openocd.exe' if os.name == 'nt' else 'openocd'}"
    template_openocd_server = (
        "{cubeide}/plugins/{latest_openocd_server}/tools/bin/" + openocd_name
    )

    template_openocd_script_path = (
        "{cubeide}/plugins/{latest_openocd_script}/resources/openocd/st_scripts"
    )

    for plugin_path in plugins_paths:
        if "mcu.externaltools.openocd" in plugin_path and ".jar" not in plugin_path:
            openocd_path.append(
                template_openocd_server.format(
                    cubeide=cubeide_path, latest_openocd_server=plugin_path
                )
            )
        elif "mcu.debug.openocd" in plugin_path:
            openocd_scripts_path.append(
                template_openocd_script_path.format(
                    cubeide=cubeide_path, latest_openocd_script=plugin_path
                )
            )

    openocd_path.sort(reverse=True)
    openocd_scripts_path.sort(reverse=True)
    return {
        # Latest version of script and server and normalize to platform
        "server_path": normalize_path(openocd_path[0]),
        "scripts_path": normalize_path(openocd_scripts_path[0]),
    }


# -------------------------------- Target info ------------------------------- #


def print_help_target_reference():
    print(
        f"""\
    {prLightPurple(
        "Pasos para determinar el nombre asociado al target mediante CubeMX:")}

    1. Abri CubeMX con el proyecto
    2. En la pestaña 'Project Manager' busca 'MCU Reference'
    3. Copia y pega el nombre expresado en 'MCU Reference'
    """
    )


def get_target_db(cubeide_path):

    plugins_path = os.listdir(normalize_path(cubeide_path + "/plugins/"))

    for plugin_path in plugins_path:
        if "mcu.productdb_" in plugin_path:
            target_file_path = (
                cubeide_path
                + "/plugins/"
                + plugin_path
                + "/resources/board_def/stm32targets.xml"
            )

    target_db = {}

    try:
        tree = ET.parse(normalize_path(target_file_path))
        root = tree.getroot()

        # En este archivo se usan namespaces y se acceden con un diccionario
        ns = {"st": "http://st.com/stm32TargetDefinitions"}
        for target in root.findall("st:mcu", ns):

            target_mcu_name = target.find("st:name", ns).text
            target_svd_filename = target.find(
                "st:cpus/st:cpu/st:svd/st:name", ns).text

            target_db[target_mcu_name.upper()] = target_svd_filename

    except FileNotFoundError:
        print(
            prRed(">>> [ERROR] ")
            + " - \tNo se encontro el archivo con las definiciones de targets validos\n"
        )

    return target_db


def get_target(cubeide_path):
    print(
        prYellow(">>> [INFO]  ")
        + " -\tPara continuar"
        + prPurple(" ES NECESARIO ")
        + """que definas el target (el nombre
                del microcontrolador) y el nombre del archivo CMSIS-SVD
                asociado (este define formalmente funcionalidades, el mapa de
                registros de perifericos desde un nivel general hasta un nivel
                de definicion y de proposito de bits).
            """
        + prLightPurple(
            "\tEste nos permite ver el estado de los registros durante debug\n"
        )
    )

    OPTION_TARGET_CFG_DEFAULT = "1"
    OPTION_TARGET_CFG_CUBEMX = "2"
    OPTION_TARGET_CFG_TABLE = "3"
    OPTION_TARGET_CFG_ABORT = "4"

    options_target_cfg = {
        OPTION_TARGET_CFG_DEFAULT: "Utilizar el STM32F103RBTx (Nucleo-F103)",
        OPTION_TARGET_CFG_CUBEMX: "Utilizar CubeMX para encontrar el nombre",
        OPTION_TARGET_CFG_TABLE: "Utilizar una tabla de targets disponibles",
    }
    option = wait_for_custom_choice(
        options_target_cfg, OPTION_TARGET_CFG_ABORT)

    target_db = get_target_db(cubeide_path)

    if option == OPTION_TARGET_CFG_DEFAULT:
        target = {"target_name": "STM32F103RBTx",
                  "target_svd": "STM32F103.svd"}
    elif option == OPTION_TARGET_CFG_CUBEMX:
        print_help_target_reference()
        target = get_target_name_from_user(target_db)
    elif option == OPTION_TARGET_CFG_TABLE:
        target = get_target_name_from_table(target_db)

    return target


def is_name_in_target_db(target_name: str, target_db: dict):
    if len(target_name) == 0:
        print(prRed(">>> [ERROR] ") + " - \tNo dejes vacio el nombre\n")
        return False

    if target_db.get(target_name.upper()) is None:
        print(
            prRed(">>> [ERROR] ")
            + " - \tEl nombre ingresado no existe en la base de datos\n"
        )
        return False

    return True


def get_target_name_from_user(target_db):
    target_name = get_valid_input(
        prompt_message="Ingresa el nombre del target a utilizar (Ej: STM32F103RBTx)",
        input_message="Target: ",
        validation_function=lambda name: is_name_in_target_db(name, target_db),
    )
    return {'target_name': target_name, 'target_svd': target_db[target_name.upper()]}


def get_target_name_from_table(target_db):
    target_print_table(target_db)
    target_name = get_valid_input(
        prompt_message="Ingresa el numero del target a utilizar (Ej: 281 = STM32F103RBTx)",
        input_message="Numero de MCU: ",
        validation_function=lambda number: is_in_range_target_db(
            number, target_db),
    )
    return {'target_name': target_name, 'target_svd': target_db[target_name.upper()]}


def paginate_list(data_list, columns=5, rows_per_page=20):
    total_items = len(data_list)
    total_pages = (total_items + (columns * rows_per_page) -
                   1) // (columns * rows_per_page)

    current_page = 0

    while True:
        start = current_page * (columns * rows_per_page)
        end = start + (columns * rows_per_page)
        sublist = data_list[start:end]

        if not sublist:
            print("No hay mas para mostrar")
            break

        print("+" + "-" * 22 + "+" + "-" * 22 + "+" + "-" * 22 +
              "+" + "-" * 22 + "+" + "-" * 22 + "+")

        for i in range(0, len(sublist), columns):
            row = sublist[i: i + columns]
            print("|", end="")
            print(
                "|".join(
                    prGreen(f"{idx+1:4}) ") + f"{name.ljust(16)}"
                    for idx, name in row
                ),
                end="|\n",
            )

        print("+" + "-" * 22 + "+" + "-" * 22 + "+" + "-" * 22 +
              "+" + "-" * 22 + "+" + "-" * 22 + "+")
        print(
            f" Page {current_page + 1} of {total_pages}  (Presiona [Enter] para siguiente, 'q' para salir) "
        )

        option = input()
        if option.lower() == "q":
            break
        current_page += 1
        if current_page >= total_pages:
            break


def target_print_table(target_db: dict):
    mcu_list = [(i, mcu) for i, mcu in enumerate(target_db.keys())]
    paginate_list(mcu_list, 5, 25)


def is_in_range_target_db(number: str, target_db):

    if len(number) == 0:
        print(prRed(">>> [ERROR] ") + " - \tNo dejes vacio el numero\n")
        return False

    if not number.isnumeric() or int(number) <= 0:
        print(prRed(">>> [ERROR] ") +
              f" - \tIngresa unicamente numeros, mayores a 0 y menores a {len(target_db)}\n")
        return False

    if int(number) > len(target_db):
        print(
            prRed(">>> [ERROR] ")
            + " - \tEl numero elegido no se encuentra en la base de datos mostrada\n"
        )
        return False

    print(
        prYellow(">>> [INFO]  ") +
        f" -\tElegiste: {list(target_db.keys())[int(number)-1]}\n"
    )
    return True


if __name__ == "__main__":

    if (not is_script_first_run()):
        not_first_run_msg()
        exit(0)

    welcome_msg()

    cubeide_path = get_cubeide_path()

    openocd = get_openocd(cubeide_path)
    print(H_LINE)

    target = get_target(cubeide_path)
    print(H_LINE)

    openocd_config = get_openocd_server_config()
    print(H_LINE)


    remove_syscall_link()
    print(prRed(">>> [REMOVE]") +
          " - Se elimina de la lista de compilacion y linking syscalls.c")

    # add_linking_options(GCC_ARM_NONE_EABI_LINKER_OPTIONS)
    print(prGreen(">>> [ADD]   ") +
          " - Se agregan flags de linking para rdimon")
    print(prGreen(">>> [ADD]   ") +
          " - Se agregan flags de linking para evitar syscalls manejadas por el target")

    set_openocd_vscode_task(

        open_ocd_server_path=openocd['server_path'],
        open_ocd_scripts_path=openocd['scripts_path'],

        open_ocd_debug_cfg_path=normalize_path(openocd_config),

        target_mcu_name=target['target_name'],
        target_mcu_svd_filename=target['target_svd'],
    )
    print(prGreen(">>> [ADD]   ") + " - Se configura el servidor de OpenOCD")
    print(prGreen(">>> [ADD]   ") +
          " - Se configura monitor en modo semihosting")


# PATH_SETTINGS_JSON = ".vscode/settings.json"  # Opcional si tiene instalada la extension "Task Buttons"
