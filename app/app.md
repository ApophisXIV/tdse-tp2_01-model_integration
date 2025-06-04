# app.c (app.h)
Endless loops, which execute tasks with fixed computing time. This sequential execution is only deviated from when an interrupt event occurs.

## Declaracion de estructuras

Se declaran las estructuras de tareas y datos auxiliares de las mismas para la medicion del tiempo critico de ejecucion

## Handles
Se implementa la lista de ejecucion de tareas con sus handles (task_x_init, task_x_update, parameters)

## Identifiers
De forma anexa se declaran constantes auxiliares con strings que describen tanto el sistema como la aplicacion

## app_init( )
Se inicializan las tareas con los parametros definidos en task_cfg_list (en este caso nulos/ninguno). Luego se inicializa mediante la macro `cycle_counter_init()` el Data Watchpoint Trigger (`DWT`) que habitualmente se activa cuando se utiliza en modo debug en caso forzamos su activacion para utilizarlo como herramienta de medicion de ciclos (dependiente de `SYSTEM_CLOCK`) de ejecucion de las tareas. Posteriormente este último será de utilidad para la medición de tiempo de ejecución de una tarea en microsegundos

## app_update( )
Se implementa un _scheduler coperativo_ (ejecutor ciclico de tareas) que permitira la ejecución de las tareas en los tiempos que tienen definidos dentro de task_x.c (`TASK_x_CNT_MAX`).
Esta función se encarga de verificar si ha transcurrido el tiempo correspondiente para ejecutar un nuevo ciclo del _scheduler_.
A continuación, recorre la lista de tareas (`task_cfg_list`) y ejecuta cada una a través de su puntero a función `task_update`, pasando como argumento sus parámetros asociados.
A su vez, en cada tarea, se encarga de medir el ultimo tiempo de ejecucion en microsegundos y actualiza los máximos encontrados en el campo `WCET` de la tarea. Finalmente se imprime por consola información de debug con el contador de ejecución y el tiempo de cada tarea

## HAL_SYSTICK_Callback( )
En esta funcion se incrementa el contador de ticks global para las tareas del sensor, el sistema, el actuador y para la aplicacion en general al ritmo del `SysTick` (1 tick/ms)