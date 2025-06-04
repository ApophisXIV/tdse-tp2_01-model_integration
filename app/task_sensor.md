# task_sensor.c (task_sensor.h, task_sensor_attribute.h) 

Non-Blocking & Update By Time Code -> Sensor Modeling

En este archivo se implementa la tarea del sensor, que es no bloqueante y se actualiza por tiempo.
La tarea del sensor se encarga de simular la lectura digital de un sensor mediante un botón y modelar su comportamiento mediante una FSM
representada por las transiciones de estado definidas en `task_sensor_attribute.h`.

En el codigo presentado a continuacion se muestra la implementacion de la maquina de estados, esta modela el comportamiento de un boton al cual al momento de transicionar de un estado estable (ST_BTN_XX_UP o ST_BTN_XX_DOWN) a un estado inestable (ST_BTN_XX_FALLING o ST_BTN_XX_RISING) se le asigna un tiempo de debounce definido por `tick_max` en la configuracion del sensor. De este modo se logra filtrar ruido y evitar lecturas erroneas del sensor.

Al finalizar el tiempo de debounce, se emite un evento al sistema para notificar el cambio de estado del sensor.

La comunicacion entre la tarea del sensor N y el sistema se realiza a traves de señales definidas en `task_sensor_attribute.h`, las cuales son enviadas al sistema mediante la funcion `put_event_task_system()` que responde a una estructura de cola de eventos (sin prioridad).

```c
for (index = 0; SENSOR_DTA_QTY > index; index++) {
    /* Update Task Sensor Configuration & Data Pointer */
    p_task_sensor_cfg = &task_sensor_cfg_list[index];
    p_task_sensor_dta = &task_sensor_dta_list[index];

    if (p_task_sensor_cfg->pressed == HAL_GPIO_ReadPin(p_task_sensor_cfg->gpio_port, p_task_sensor_cfg->pin)) {
        p_task_sensor_dta->event = EV_BTN_XX_DOWN;
    } else {
        p_task_sensor_dta->event = EV_BTN_XX_UP;
    }

    switch (p_task_sensor_dta->state) {
    case ST_BTN_XX_UP:
        if (EV_BTN_XX_DOWN == p_task_sensor_dta->event) {
            p_task_sensor_dta->state = ST_BTN_XX_FALLING;
            p_task_sensor_dta->tick  = p_task_sensor_cfg->tick_max;
        }
        break;

    case ST_BTN_XX_FALLING:
        if ((EV_BTN_XX_DOWN == p_task_sensor_dta->event || EV_BTN_XX_UP == p_task_sensor_dta->event) && p_task_sensor_dta->tick > 0) {
            p_task_sensor_dta->tick--;
        } else {    // EV_BTN_XX_UP or EV_BTN_XX_DOWN and elapsed debounce time [tick==0]
            p_task_sensor_dta->state = ST_BTN_XX_DOWN;
            put_event_task_system(p_task_sensor_cfg->signal_down);
        }
        break;

    case ST_BTN_XX_DOWN:
        if (EV_BTN_XX_UP == p_task_sensor_dta->event) {
            p_task_sensor_dta->state = ST_BTN_XX_RISING;
            p_task_sensor_dta->tick  = p_task_sensor_cfg->tick_max;
        }
        break;

    case ST_BTN_XX_RISING:
        if ((EV_BTN_XX_DOWN == p_task_sensor_dta->event || EV_BTN_XX_UP == p_task_sensor_dta->event) && (p_task_sensor_dta->tick > 0)) {
            p_task_sensor_dta->tick--;
        } else {    // EV_BTN_XX_UP or EV_BTN_XX_DOWN and elapsed debounce time [tick==0]
            p_task_sensor_dta->state = ST_BTN_XX_UP;
            put_event_task_system(p_task_sensor_cfg->signal_up);
        }
        break;

    default:

        break;
    }
}
```