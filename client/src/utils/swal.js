import Swal from 'sweetalert2';

export const errorWithoutBtn = (title, text) => {
  Swal.fire({
    icon: 'error',
    title: title,
    text: text,
    showConfirmButton: false,
    timer: 2000
  });
}

export const successWithoutBtn = (title, text, cb) => {
  Swal.fire({
    icon: 'success',
    title: title,
    text: text,
    showConfirmButton: false,
    timer: 2000
  }).then(() => cb())
}

export const warningWithoutBtn = (title, text) => {
  Swal.fire({
    icon: 'warning',
    title: title,
    text: text,
    showConfirmButton: false,
    timer: 2000
  })
}

export const cancelAlert = (title, text, btn1, btn2, cb) => {
  Swal.fire({
    icon: 'warning',
    title: title,
    text: text,
    showCancelButton: true,
    confirmButtonText: btn1,
    cancelButtonText: btn2
  }).then((res) => {
    if (res.isConfirmed) cb();
  })
}