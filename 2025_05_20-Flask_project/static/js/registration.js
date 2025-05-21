 const apiUrl = '/items';

    document.addEventListener('DOMContentLoaded', () => {
      loadItems();

      document.getElementById('addItemForm').addEventListener('submit', e => {
        e.preventDefault();
        const name = document.getElementById('itemName').value;
        const price = parseInt(document.getElementById('itemPrice').value);
        const quantity = parseInt(document.getElementById('itemQuantity').value);

        fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, price, quantity })
        })
        .then(res => res.json())
        .then(() => {
          loadItems();
          document.getElementById('addItemForm').reset();
        });
      });
    });
    function loadItems() {
      fetch(apiUrl)
        .then(res => res.json())
        .then(data => {
          const tbody = document.getElementById('itemTableBody');
          tbody.innerHTML = '';
          data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
              <td>${item.item_id}</td>
              <td><input class="table-input" type="text" value="${item.name}" id="name-${item.item_id}"></td>
              <td><input class="table-input" type="number" value="${item.price}" id="price-${item.item_id}"></td>
              <td><input class="table-input" type="number" value="${item.quantity}" id="quantity-${item.item_id}"></td>
              <td><button class="update" onclick="updateItem(${item.item_id})">수정</button></td>
              <td><button class="delete" onclick="deleteItem(${item.item_id})">삭제</button></td>
            `;
            tbody.appendChild(tr);
          });
        });
    }

    function updateItem(id) {
      const name = document.getElementById(`name-${id}`).value;
      const price = parseInt(document.getElementById(`price-${id}`).value);
      const quantity = parseInt(document.getElementById(`quantity-${id}`).value);

      fetch(`${apiUrl}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, price, quantity })
      })
      .then(res => res.json())
      .then(() => loadItems());
    }

    function deleteItem(id) {
      if (confirm('정말 삭제하시겠습니까?')) {
        fetch(`${apiUrl}/${id}`, {
          method: 'DELETE'
        })
        .then(res => res.json())
        .then(() => loadItems());
      }
    }