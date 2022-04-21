if (document.querySelector('.lk-form')) {
    document.querySelector('form').className = "list-group-item shadow-money rounded"

    let temp = document.querySelector('#id_username')
    if (temp) temp.classList.add('form-control')

    temp = document.querySelector('#id_password')
    if (temp) temp.classList.add('form-control')

    temp = document.querySelector('#id_email')
    if (temp) temp.classList.add('form-control')

    temp = document.querySelector('#id_password1')
    if (temp) temp.classList.add('form-control')

    temp = document.querySelector('#id_password2')
    if (temp) temp.classList.add('form-control')

    temp = document.querySelector('#id_new_password1')
    if (temp) temp.classList.add('form-control')

    temp = document.querySelector('#id_new_password2')
    if (temp) temp.classList.add('form-control')

    temp = document.querySelector('.helptext')
    if (temp) temp.remove()
}

if (document.querySelector('.lk-form-send')) {
    document.querySelector('.lk-form-send').className = "list-group-item shadow-money rounded"
}
