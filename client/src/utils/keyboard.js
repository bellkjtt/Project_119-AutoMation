// 스페이스 막기
export const blockSpace = (e) => {
    if (e.key === ' ') e.preventDefault();
}

// 엔터 키 입력
export const enterKey = (e, cb) => {
    if (e.key === 'Enter') cb();
}