from vk_api.keyboard import VkKeyboard, VkKeyboardColor


keyboard_start = VkKeyboard(one_time=True)
keyboard_start.add_button('Искать', VkKeyboardColor.PRIMARY)

keyboard_second = VkKeyboard(one_time=True)
keyboard_second.add_button('просмотр', VkKeyboardColor.PRIMARY)

keyboard_main = VkKeyboard(one_time=False)
keyboard_main.add_button('назад', VkKeyboardColor.SECONDARY)
keyboard_main.add_button('вперед', VkKeyboardColor.SECONDARY)
keyboard_main.add_line()
keyboard_main.add_button('в избранное', VkKeyboardColor.POSITIVE)
keyboard_main.add_button('посмотреть избранное', VkKeyboardColor.POSITIVE)
keyboard_main.add_line()
keyboard_main.add_button('в чёрный список', VkKeyboardColor.NEGATIVE)
