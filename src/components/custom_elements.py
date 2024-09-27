import dash_mantine_components as dmc


def create_switch_card(switch_id, label, description):
    return dmc.Card(
        dmc.Group(
            [
                dmc.Stack(
                    [dmc.Text(label, size="md"), dmc.Text(description, c="dimmed", size="xs", ta="right")],
                    gap=0.1,
                ),
                # dmc.Switch(id=switch_id, label=label, description=description, labelPosition="left"),
                dmc.Switch(id=switch_id),
            ],
            justify="space-around",
            gap="xl",
        ),
        withBorder=True,
        padding=7,
    )
