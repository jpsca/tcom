from oot import Component


class Button(Component):
    type: str

    PRIMARY_CLASSES = (
        "disabled:bg-purple-300",
        "focus:bg-purple-600",
        "hover:bg-purple-600",
        "bg-purple-500",
        "text-white",
    )
    OUTLINE_CLASSES = (
        "hover:bg-gray-200",
        "focus:bg-gray-200",
        "disabled:bg-gray-100",
        "bg-white",
        "border",
        "border-purple-600",
        "text-purple-600",
    )
    DANGER_CLASSES = (
        "hover:bg-red-600",
        "focus:bg-red-600",
        "disabled:bg-red-300",
        "bg-red-500",
        "text-white",
    )
    BASE_CLASSES = (
        "cursor-pointer",
        "rounded",
        "transition",
        "duration-200",
        "text-center",
        "p-4",
        "whitespace-nowrap",
        "font-bold",
    )

    BUTTON_TYPE_MAPPINGS = {
        "primary": PRIMARY_CLASSES,
        "danger": DANGER_CLASSES,
        "outline": OUTLINE_CLASSES
    }

    def init(self):
        self.classes = " ".join(self.BUTTON_TYPE_MAPPINGS[self.type] + self.BASE_CLASSES)
