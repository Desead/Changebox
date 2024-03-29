"use strict"

const url_domain = location.origin + '/'
const url_api = 'api/v1/'
const url_rates = 'rates/'
const url_direct = 'direct/'
let rates
let left_money_select = {}
let right_money_select = {}
const TIME_REFRESH_IN_MSEC = 30000

function SetSelectFirstMoney() {
    // разовое начальное выделение монеткы слева. В дальнейшем выделение есть всегда и эта функция более не используется
    let temp = document.querySelectorAll('.item_select')
    for (let i of temp) {
        if (i.parentNode.classList.contains('change_left_dn')) return
    }
    temp = document.querySelector('.change_left_dn').firstChild
    temp.classList.add('item_select')

    left_money_select['id'] = temp.id
    if (temp.classList.contains('crypto')) {
        left_money_select['type'] = 'crypto'
    } else if (temp.classList.contains('fiat')) {
        left_money_select['type'] = 'fiat'
    }
    for (let i of temp.firstChild.children) {
        if (i.classList.contains('money_change_title')) {
            left_money_select['title'] = i.innerHTML
        }
    }
    CreateRightMoney()
}

function SetItemSelect() {
    const menu = this.parentNode
    for (let i of menu.children) i.classList.remove('item_select')
    this.classList.add('item_select')

    if (menu.classList.contains('change_left_dn')) {
        left_money_select['id'] = this.id
        if (this.classList.contains('crypto')) {
            left_money_select['type'] = 'crypto'
        } else if (this.classList.contains('fiat')) {
            left_money_select['type'] = 'fiat'
        }
        for (let i of this.firstChild.children) {
            if (i.classList.contains('money_change_title')) {
                left_money_select['title'] = i.innerHTML
            }
        }
        // Если  выделение слева изменилось, то выделение справа сбрасываем
        right_money_select = {}
    } else {
        if (menu.classList.contains('change_right_dn')) {
            right_money_select['id'] = this.id
            if (this.classList.contains('crypto')) {
                right_money_select['type'] = 'crypto'
            } else if (this.classList.contains('fiat')) {
                right_money_select['type'] = 'fiat'
            }
            for (let i of this.firstChild.children) {
                if (i.classList.contains('money_change_title')) {
                    right_money_select['title'] = i.innerHTML
                }
            }
        }
    }
}

function GetLeftSelectedMoney() {
    // сохранили выделение для монетки слева
    let temp = document.querySelectorAll('.item_select')

    for (let i of temp) {
        if (i.parentNode.classList.contains('change_left_dn')) return i
    }
    alert('Не выделен ни один элемент. Ошибка')
}

function CreateMoney(p_node, money_name, money_id, money_type, img_path, reserv_num = 0) {
    /*  Создаём компонент монетку
    p_node      родительская нода к которой прицепляемся
    money_name  название монетки для сайта
    money_id    xml код монетки
    money_type  тип монетки
    img_path    путь к лого
    return      возвращем созданный элемент
     */
    let div_money_name = document.createElement('div')
    div_money_name.className = 'money_change_title'
    let elem_text = document.createTextNode(money_name)
    div_money_name.append(elem_text)

    let div_money_img = document.createElement('div')
    div_money_img.className = 'money_change_img'
    let money_img = document.createElement('img')
    money_img.setAttribute('height', '30')
    money_img.setAttribute('width', 'auto')
    money_img.setAttribute('src', img_path)
    div_money_img.append(money_img)

    let div_money = document.createElement('div')
    div_money.className = 'money'
    div_money.append(div_money_img)
    div_money.append(div_money_name)

    let elem_list = document.createElement('a')
    elem_list.setAttribute('href', '#')
    if (money_id !== '') elem_list.setAttribute('id', money_id)
    elem_list.className = 'list-group-item list-group-item-action shadow-money rounded reserv_link ' + money_type
    elem_list.append(div_money)

    if (reserv_num > 0) {
        let reserv = document.createElement('div')
        reserv.className = 'reserv_site'
        let reserv_text = document.createElement('p')
        reserv_text.innerText = reserv_num
        reserv.append(reserv_text)
        elem_list.append(reserv)
    }

    p_node.append(elem_list)

    return elem_list
}

function HideMoney() {
    // скрываем монетки по фильтру: All, fiat, Crypto
    let temp

    if (this.parentNode.classList.contains('change_left_up')) temp = document.querySelector('.change_left_dn').children
    if (this.parentNode.classList.contains('change_right_up')) temp = document.querySelector('.change_right_dn').children

    let class_view = this.textContent.toLowerCase()
    if (class_view === 'all') {
        for (let i of temp) i.style.display = ''
    } else {
        for (let i of temp) {
            if (i.classList.contains(class_view)) {
                i.style.display = ''
            } else {
                i.style.display = 'none'
            }
        }
    }
}

async function CreateRightMoney() {
    const parent = document.querySelector('.change_right_dn')
    while (parent.firstChild) {
        parent.firstChild.remove()
    }

    //ищем фильтр для монеток справа
    let class_view
    for (let i of document.querySelector('.change_right_up').children) {
        if (i.classList.contains('item_select')) {
            class_view = i.textContent.toLowerCase()
            break
        }
    }

    for (let money of rates[GetLeftSelectedMoney().id]) {
        const elem = CreateMoney(document.querySelector('.change_right_dn'), money['name_right'], money['right'], money['type_right'], money['img_right'], money['reserv'])
        if (!money['active']) {
            elem.classList.add('disabled')
        }
        elem.addEventListener('click', SetItemSelect)
        elem.addEventListener('click', SwapDelNew)


        if (class_view !== 'all') if (class_view !== money['type_right']) elem.style.display = 'none'
    }
}

async function GetRates(url) {
    try {
        const response = await fetch(url)
        if (response.ok) {
            return await response.json()
        }
    } catch (e) {
        // console.log('Error get data from', url, e)
        return false
    }
}

async function MainLoop() {
    if (document.location.pathname !== '/')
        return

    //все новые монетки
    rates = await GetRates(url_domain + url_api + url_rates)

    try {
        if (!rates)
            return

        if (Boolean(rates['error'])) {
            return
        }
    } catch (e) {
        return
    }


    //дополнительный массив с названиями новых монеток, нужен чтобы не портить начальынй объект rates и показывать
    //из него монетки справа
    let rates_money_name = []
    for (let name in rates) rates_money_name.push(name)

    //старые монетки слева, которые уже показаны на сайте
    let old_money_left = document.querySelector('.change_left_dn')
    if (old_money_left) old_money_left = old_money_left.childNodes
    else {
        // Сюда можно добавить перерисовку главной, когда перерыв закончился
        return
    }

    //Убираем из старого массива те монетки которых нету в новом
    //а из нового то которые есть в старом.
    //в итоге в новом останется только то, что надо добавить слева
    for (let i = old_money_left.length - 1; i >= 0; i--) {
        if (rates[old_money_left[i].id] === undefined) {
            old_money_left[i].remove()
        } else {
            rates_money_name.splice(rates_money_name.indexOf(old_money_left[i].id), 1)
        }
    }

    // создаём монетки слева
    for (let money in rates) {
        // если текущей монеты нет в массиве rates_money_nameзначит добавлять её не надо
        if (rates_money_name.indexOf(money) < 0) continue
        const elem = CreateMoney(document.querySelector('.change_left_dn'), rates[money][0]['name_left'], money, rates[money][0]['type_left'], rates[money][0]['img_left'])
        elem.addEventListener('click', SetItemSelect)
        elem.addEventListener('click', CreateRightMoney)
    }
    SetSelectFirstMoney()
}

function CreateSwapBlock(direct) {
    const main_block = document.querySelector('.change_swap_dn')
    const template_block = document.querySelector('#template_change')
    main_block.append(template_block.content.cloneNode(true))

    document.querySelector('#swap_left').innerHTML = 'Отдаёте: <b>' + left_money_select['title'] + '</b>'
    document.querySelector('#swap_left_min').innerHTML = direct['min_left']
    document.querySelector('#swap_left_max').innerHTML = direct['max_left']

    document.querySelector('#swap_right').innerHTML = 'Получаете: <b>' + right_money_select['title'] + '</b>'
    document.querySelector('#swap_right_min').innerHTML = direct['min_right']
    document.querySelector('#swap_right_max').innerHTML = direct['max_right']

    // добавляем дополнительнрые поля
    let count = 1
    let temp = direct['add_left']
    for (let i of temp) {
        let add_field = document.createElement('input')
        add_field.className = 'form-control'
        add_field.setAttribute('type', 'text')
        add_field.setAttribute('required', '')
        add_field.setAttribute('placeholder', i)
        add_field.setAttribute('name', 'add_in_' + String(count))
        document.querySelector('#left_fields').append(add_field)
        count++
    }
    count = 1
    temp = direct['add_right']
    for (let i of temp) {
        let add_field = document.createElement('input')
        add_field.className = 'form-control'
        add_field.setAttribute('type', 'text')
        add_field.setAttribute('required', '')
        add_field.setAttribute('placeholder', i)
        add_field.setAttribute('name', 'add_out_' + String(count))
        document.querySelector('#right_fields').append(add_field)
        count++
    }

    //запоминаем курс обмена
    left_money_select['rate'] = direct['rate_left_final']
    right_money_select['rate'] = direct['rate_right_final']

    //вешаем событие на поля сумм
    document.querySelector('#left_sum').addEventListener('blur', SumToSum)
    document.querySelector('#right_sum').addEventListener('blur', SumToSum)
    document.querySelector('#left_sum').addEventListener('change', SumToSum)
    document.querySelector('#right_sum').addEventListener('change', SumToSum)
    document.querySelector('#left_sum').addEventListener('focus', SumToSum)
    document.querySelector('#right_sum').addEventListener('focus', SumToSum)

    //изменяем атрибуты точности у полей сумма
    if (left_money_select['type'] === 'crypto')
        document.querySelector('#left_sum').setAttribute('step', '0.00000001')
    if (right_money_select['type'] === 'crypto')
        document.querySelector('#right_sum').setAttribute('step', '0.00000001')

    SEOSet(direct['seo_title'], direct['seo_descriptions'], direct['seo_keywords'])


    document.querySelector('#money_left').value = left_money_select['id']
    document.querySelector('#money_right').value = right_money_select['id']
}

function SEOSet(title, descriptions, keywords) {
    if (title !== '')
        document.querySelector("title").innerHTML = title
    if (keywords !== '')
        document.querySelector("meta[name='keywords']").setAttribute("content", keywords)
    if (descriptions !== '')
        document.querySelector("meta[name='description']").setAttribute("content", descriptions)
}

function SumToSum() {
    //Меняем сумму в одном и сразу автоматом меняется курс в другом поле
    const left = document.querySelector('#left_sum')
    const right = document.querySelector('#right_sum')

    let left_num = left.value
    let right_num = right.value

    if (left === this)
        right_num = left_num * right_money_select['rate'] / left_money_select['rate']

    if (right === this)
        left_num = right_num * left_money_select['rate'] / right_money_select['rate']


    if (left_money_select['type'] === 'fiat') left.value = (+left_num).toFixed(2)
    else left.value = (+left_num).toFixed(8)
    if (right_money_select['type'] === 'fiat') right.value = (+right_num).toFixed(2)
    else right.value = (+right_num).toFixed(8)
}

function CheckMinmax() {
    // проверяем соответствие введённых сумм ограничениям мин-макс
    const send_pay = document.querySelector('#send_pay')
    send_pay.setAttribute('type', 'button')

    const min_left = document.querySelector('#swap_left_min')
    const max_left = document.querySelector('#swap_left_max')
    const min_right = document.querySelector('#swap_right_min')
    const max_right = document.querySelector('#swap_right_max')

    const left_sum = document.querySelector('#left_sum')
    const right_sum = document.querySelector('#right_sum')

    let error_flag = false
    if (+left_sum.value < +min_left.innerText || +left_sum.value > +max_left.innerText) {
        left_sum.classList.add('red_border')
        error_flag = true
    } else left_sum.classList.remove('red_border')

    if (+right_sum.value < +min_right.innerText || +right_sum.value > +max_right.innerText) {
        right_sum.classList.add('red_border')
        error_flag = true
    } else right_sum.classList.remove('red_border')

    if (error_flag) return false

    send_pay.setAttribute('type', 'submit')
}

//      swap            //////////////////////////////////////////////////
async function SwapDelNew() {
    if (left_money_select['id'] !== undefined && right_money_select['id'] !== undefined) {
        const url = url_domain + url_api + url_direct + '?' + new URLSearchParams({
            'cur_from': left_money_select['id'],
            'cur_to': right_money_select['id'],
        })
        const direct = await GetRates(url)

        if (Boolean(rates['error'])) {
            return
        }

        let temp = document.querySelector('.change_swap_dn').children
        for (let i = temp.length - 1; i >= 0; i--) {
            temp[i].remove()
        }
        //отображаем блок обмена
        CreateSwapBlock(direct)
    }
}

//      main loop       //////////////////////////////////////////////////
for (let i of document.querySelectorAll('.menu_item')) {
    i.addEventListener('click', SetItemSelect)
    i.addEventListener('click', HideMoney)
}

MainLoop()
if (location.hostname === '127.0.0.1') {
    setInterval(MainLoop, 5000)
} else {
    setInterval(MainLoop, TIME_REFRESH_IN_MSEC)
}


// function MinLeftToInput() {
//     document.querySelector('#left_sum').value = document.querySelector('#swap_left_min').innerText
// }
//
// function MaxLeftToInput() {
//     document.querySelector('#left_sum').value = document.querySelector('#swap_left_max').innerText
// }
//
// function MinRightToInput() {
//     document.querySelector('#right_sum').value = document.querySelector('#swap_right_min').innerText
// }
//
// function MaxRightToInput() {
//     document.querySelector('#right_sum').value = document.querySelector('#swap_right_max').innerText
// }

