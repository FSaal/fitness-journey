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


def segmented_control(title=None, description=None, **kwargs):
    """Super segmentedControl element, with added title and description ability (similar to select)."""
    layout = dmc.Stack(
        [
            dmc.Text(title, fw=475, size="sm") if title else None,
            dmc.Text(description, c="dimmed", size="xs") if description else None,
            dmc.SegmentedControl(**kwargs),
        ],
        gap=1,
    )
    return layout
