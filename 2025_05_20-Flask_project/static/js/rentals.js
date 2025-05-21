window.onload = async function () {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById("rentalDate").value = today;
    const userSelect = document.getElementById("userSelect");
    const itemSelect = document.getElementById("itemSelect");
    try {
      // 사용자 목록 로드
      const userRes = await fetch('/users'); 
      if (!userRes.ok) throw new Error("사용자 목록 불러오기 실패");
      const users = await userRes.json();
      users.forEach(user => {
        const option = document.createElement("option");
        option.value = user.user_id;
        option.textContent = user.name;
        userSelect.appendChild(option);
      });
      // 물품 목록 로드
      const itemRes = await fetch('/items'); 
      if (!itemRes.ok) throw new Error("물품 목록 불러오기 실패");
      const items = await itemRes.json();
      items.forEach(item => {
        const option = document.createElement("option");
        option.value = item.item_id;
        const priceNum = Number(item.price);
        option.textContent = `${item.name} (${priceNum.toLocaleString()}원)`;
        option.setAttribute("data-price", priceNum);
        itemSelect.appendChild(option);
      });

      // 대여 현황도 같이 불러오기
      await loadRentalStatus();

    } catch (error) {
      alert("데이터 로딩 실패");
      console.error(error);
    }
  };

  document.getElementById("itemSelect").addEventListener("change", function () {
    const selected = this.options[this.selectedIndex];
    const price = selected.getAttribute("data-price");
    document.getElementById("price").value = price ? `${price} 원` : "";
  });

  function formatDate(dateStr) {
  const d = new Date(dateStr);
  const year = d.getFullYear();
  const month = d.getMonth() + 1;
  const day = d.getDate();

  return `${year}년 ${month}월 ${day}일`;
}


  // 대여하기 제출
  document.getElementById("rentalForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = {
      user_id: document.getElementById("userSelect").value,
      item_id: document.getElementById("itemSelect").value,  // 기존 오타 수정
      rent_date: document.getElementById("rentalDate").value,
      price: parseInt(document.getElementById("price").value.replace(" 원", "")),
      status: "대여중"
    };

    try {
      const res = await fetch('/api/rentals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (res.ok) {
        alert("대여가 완료되었습니다.");
        // location.reload() 대신 현황만 갱신
        await loadRentalStatus();
        this.reset();
        document.getElementById("rentalDate").value = new Date().toISOString().split('T')[0];
        document.getElementById("price").value = "";
      } else {
        alert("대여 처리 실패");
      }
    } catch (err) {
      alert("서버 오류 발생");
      console.error(err);
    }
  });

  // 대여 현황 불러오기 함수
  async function loadRentalStatus() {
    try {
      const res = await fetch('/api/rentals');
      if (!res.ok) throw new Error('대여현황 불러오기 실패');
      const rentals = await res.json();

      const tbody = document.querySelector("#rentalStatusTable tbody");
      tbody.innerHTML = "";  // 초기화

  rentals.forEach(rental => {
    const tr = document.createElement("tr");

  tr.innerHTML = `
    <td>${rental.user_name || rental.user_id}</td>
    <td>${rental.item_name || rental.item_id}</td>
    <td>${formatDate(rental.rent_date)}</td>
    <td>${Number(rental.price).toLocaleString()}</td>
    <td class="${rental.status === '대여중' ? 'rented' : 'returned'}">${rental.status}</td>
    <td>
      ${rental.status === '대여중' ? `<button class="return-btn" data-id="${rental.rental_id}">반납</button>` : ''}
    </td>
  `;

  tbody.appendChild(tr);
});

      // 반납 버튼 이벤트 등록
      document.querySelectorAll('.return-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
          const rentalId = e.target.getAttribute('data-id');
          if (!confirm('이 물건을 반납 처리하시겠습니까?')) return;

          try {
            // 반납 API 호출 (백엔드 경로에 맞게 수정)
            const res = await fetch(`/api/rentals/${rentalId}/return`, {
              method: 'PUT'
            });
            if (res.ok) {
              alert('반납 처리되었습니다.');
              await loadRentalStatus();
            } else {
              alert('반납 처리 실패');
            }
          } catch (err) {
            alert('서버 오류 발생');
            console.error(err);
          }
        });
      });

    } catch (err) {
      alert(err.message);
      console.error(err);
    }
  }