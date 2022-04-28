// Скрываем поле кол-во подтверждений для фиатной монеты и выбор тикера с binance
function ConfirmHide() {
    const confirm = document.querySelector('.field-conformation')
    const tiker = document.querySelector('.field-tiker')
    if (confirm && tiker) {
        for (let i of field_money_type) {
            if (i.selected) {
                if (i.value === 'crypto') {
                    confirm.classList.remove('hide_element')
                    tiker.classList.remove('hide_element')
                }
                if (i.value === 'fiat') {
                    confirm.classList.add('hide_element')
                    tiker.classList.add('hide_element')
                }
            }
        }
    }
}

const field_money_type = document.querySelector('#id_money_type')
if (field_money_type) field_money_type.addEventListener('click', ConfirmHide)
ConfirmHide()
////////////////////////////////////////////////////////////

// Берём help_text и делаем его ссылкой в модели Валюта+ПС (Fullmoney)
const a_link = 'https://jsons.info/signatures/currencies'

const help_text = document.querySelectorAll('.help')
if (help_text)
    for (let i of help_text) {
        if (i.innerText.indexOf(a_link) >= 0) {
            i.innerHTML = i.innerText.replace(a_link, '<a href="https://jsons.info/signatures/currencies" target="_blank">https://jsons.info/signatures/currencies</a>')
            break
        }
    }
////////////////////////////////////////////////////////////
