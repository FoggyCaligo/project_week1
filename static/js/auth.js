// 중복 체크 공통 함수
async function checkDuplicate(fieldId, msgId, endpoint) {
    const value = document.getElementById(fieldId).value.trim();
    const msgArea = document.getElementById(msgId);

    if (!value) {
        alert("내용을 입력해주세요.");
        return;
    }

    try {
        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ field: fieldId, value: value })
        });
        const data = await response.json();

        msgArea.innerText = data.message;
        msgArea.style.color = (data.result === 'success') ? "green" : "red";
    } catch (err) {
        console.error("중복 체크 에러:", err);
        alert("서버 통신 중 에러가 발생했습니다.");
    }
}

// 초기화 (DOM이 로드된 후 버튼에 이벤트 바인딩)
document.addEventListener('DOMContentLoaded', () => {
    const checkIdBtn = document.getElementById('checkIdBtn');
    const checkNickBtn = document.getElementById('checkNickBtn');

    if (checkIdBtn) {
        checkIdBtn.onclick = () => checkDuplicate('userName', 'idCheckMsg', '/check-duplicate');
    }
    if (checkNickBtn) {
        checkNickBtn.onclick = () => checkDuplicate('nickName', 'nickCheckMsg', '/check-duplicate');
    }
});