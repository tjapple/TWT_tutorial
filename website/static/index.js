function deletePost(postId) {
    fetch("/delete-post", {
        method: "POST",
        body: JSON.stringify({ postId: postId}),
    }).then((_res) => {
        window.location.href = window.location.href;
    });
}

function deleteItem(itemId) {
    fetch("/delete-item", {
        method: "POST",
        body: JSON.stringify({ itemId: itemId }),
    }).then((_res) => {
        window.location.href = window.location.href;
    });
}

function completeOrder(openOrderId) {
    fetch("/complete-order", {
        method: "POST",
        body: JSON.stringify({ openOrderId: openOrderId }),
    }).then((_res) => {
        window.location.href = window.location.href;
    });
}

function declineOrder(openOrderId) {
    fetch("/decline-order", {
        method: "POST",
        body: JSON.stringify({ openOrderId: openOrderId }),
    }).then((_res) => {
        window.location.href = window.location.href;
    });
}

function favFarm(farmId) {
    fetch("/fav-farm", {
        method: "POST",
        body: JSON.stringify({ farmId: farmId }),
    }).then((_res) => {
        window.location.href = window.location.href;
    });
}

function unFavFarm(favId) {
    fetch("/un-fav-farm", {
        method: "POST",
        body: JSON.stringify({ favId: favId }),
    }).then((_res) => {
        window.location.href = window.location.href;
    });
}

function sum() {
    var rows = document.getElementById("orderForm").rows;
    var order_total = 0;
    for (var i = 1; i < rows.length - 1; i++) {
        if (rows[i].getElementsByClassName('order')[0]?.value) {
            var unit_price = parseFloat(rows[i].getElementsByClassName('price')[0].innerHTML);
            var row_total = unit_price * parseFloat(rows[i].getElementsByClassName('order')[0].value);
            rows[i].getElementsByClassName('r_total')[0].innerHTML = '$' + row_total; 
            order_total += row_total
        }
        else {
            rows[i].getElementsByClassName('r_total')[0].innerHTML = "";
        }
    };
    document.getElementById('order_total').innerHTML = '$' + order_total;
}
