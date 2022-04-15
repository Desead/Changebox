"use strict"

const url_domain = 'http://127.0.0.1:8000/'
const url_api = 'api/v1/'
const url_rates = 'rates/'
let rates

function SetSelectFirstMoney() {
    // разовое начальное выделение монеткы слева. В дальнейшем выделение есть всегда и эта функция более не используется
    const temp = document.querySelectorAll('.item_select')
    for (let i of temp) {
        if (i.parentNode.classList.contains('change_left_dn'))
            return
    }
    document.querySelector('.change_left_dn').firstChild.classList.add('item_select')
    CreateRightMoney()
}

function SetItemSelect() {
    const menu = this.parentNode
    for (let i of menu.children)
        i.classList.remove('item_select')
    this.classList.add('item_select')
}

function CreateMoney(p_node, money_name, money_id, money_type, img_path) {
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
    money_img.setAttribute('width', '30')
    // money_img.setAttribute('alt', money_name)
    money_img.setAttribute('src', img_path)
    div_money_img.append(money_img)

    let div_money = document.createElement('div')
    div_money.className = 'money'
    div_money.append(div_money_img)
    div_money.append(div_money_name)

    let elem_list = document.createElement('a')
    elem_list.setAttribute('href', '#')
    if (money_id !== '') elem_list.setAttribute('id', money_id)
    elem_list.className = 'list-group-item list-group-item-action ' + money_type
    elem_list.append(div_money)

    p_node.append(elem_list)

    return elem_list
}

function GetLeftSelectedMoney() {
    // сохранили выделение для монетки слева
    let temp = document.querySelectorAll('.item_select')

    for (let i of temp) {
        if (i.parentNode.classList.contains('change_left_dn')) return i
    }
    // если ничего не выделено то выделяем слева первую монету. Вообще это странно что ничего не выделено
    const elements = document.querySelector('.change_left_dn').firstChild
    elements.classList.add('item_select')
    return elements
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
        const elem = CreateMoney(document.querySelector('.change_right_dn'), money['name_right'], money['right'], money['type_right'], '/static/img/c-qiwi.svg')
        elem.addEventListener('click', SetItemSelect)

        if (class_view !== 'all')
            if (class_view !== money['type_right'])
                elem.style.display = 'none'
    }
}

async function GetRates() {
    const url = url_domain + url_api + url_rates
    try {
        const response = await fetch(url)
        if (response.ok) {
            return await response.json()
        }
    } catch (e) {
        console.log('Error get data from', url, e)
    }
}

async function MainLoop() {
    //все новые монетки
    rates = await GetRates()

    //дополнительный массив с названиями новых монеток, нужен чтобы не портить начальынй объект rates и показывать
    //из него монетки справа
    let rates_money_name = []
    for (let name in rates) rates_money_name.push(name)

    //старые монетки слева, которые уже показаны на сайте
    let old_money_left = document.querySelector('.change_left_dn').childNodes

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
        const elem = CreateMoney(document.querySelector('.change_left_dn'), rates[money][0]['name_left'], money, rates[money][0]['type_left'], '/static/img/c-qiwi.svg')
        elem.addEventListener('click', SetItemSelect)
        elem.addEventListener('click', CreateRightMoney)
    }
    SetSelectFirstMoney()
}

function HideMoney() {
    let temp

    if (this.parentNode.classList.contains('change_left_up'))
        temp = document.querySelector('.change_left_dn').children
    if (this.parentNode.classList.contains('change_right_up'))
        temp = document.querySelector('.change_right_dn').children

    let class_view = this.textContent.toLowerCase()

    if (class_view === 'all') {
        for (let i of temp)
            i.style.display = ''
    } else {
        for (let i of temp) {
            if (i.classList.contains(class_view))
                i.style.display = ''
            else
                i.style.display = 'none'
        }
    }
}

////////////////////////////////////////////////////////////////////////////
for (let i of document.querySelectorAll('.menu_item')) {
    i.addEventListener('click', SetItemSelect)
    i.addEventListener('click', HideMoney)
}

MainLoop()
setInterval(MainLoop, 2000)

