var checkTicker = document.querySelector('.check-ticker');
var resultTicker = document.querySelector('.result-ticker');
var inputField = document.getElementById('tickerInput');
var outputDiv = document.getElementById('outputDiv');
var errorMessage = document.querySelector('.error-message');
var buttonNotLoadingState = document.querySelector('.buttonNotLoadingState')
var buttonLoadingState = document.querySelector('.buttonLoadingState')
var tickerNameTitle = document.getElementById('tickerNameTitle');
var recommend = document.getElementById('recommend');
var notRecommend = document.getElementById('notRecommend');
var tickerDays = document.getElementById('tickerDays');
var tickerDaysSelectedValue = '6'

function setButtonLoadingState() {
    buttonNotLoadingState.style.display = "none"
    buttonLoadingState.style.display = "inline-block"
}

function removeButtonLoadingState() {
    buttonNotLoadingState.style.display = "block"
    buttonLoadingState.style.display = "none"
}

tickerDays.addEventListener('change', function() {
    tickerDaysSelectedValue = tickerDays.value;
});

function postData() {
    if (inputField.value !== "") {
        // var selectedValue = '5'
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/fetch", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.setRequestHeader("ticker", inputField.value);
        xhr.setRequestHeader("days", tickerDaysSelectedValue);

        setButtonLoadingState()

        if (window.getComputedStyle(errorMessage).display === "block") {
            errorMessage.style.display = "none";
            errorMessage.innerHTML = ""
            errorMessage.classList.remove("animate__animated", "animate__fadeInDown");
        }

        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);


                tickerNameTitle.innerHTML = inputField.value

                if (response.recommendation === "no") {
                    recommend.style.display = "none"
                    notRecommend.style.display = "block"
                    var notBuyReason = document.getElementById('notBuyReason');
                    notBuyReason.innerHTML = response.reason
                } else {
                    var sellPrice = document.getElementById('sellPrice');
                    var additionalBuyPrice = document.getElementById('additionalBuyPrice');
                    var stopLossPrice = document.getElementById('stopLossPrice');
                    var investPeriod = document.getElementById('investPeriod');
                    var buyReason = document.getElementById('buyReason');

                    recommend.style.display = "block"
                    notRecommend.style.display = "none"

                    buyReason.innerHTML = response.reason
                    sellPrice.innerHTML = response.target_sell_price
                    additionalBuyPrice.innerHTML = response.additional_buy_price
                    stopLossPrice.innerHTML = response.stop_loss_price
                    investPeriod.innerHTML = response.investment_period

                }

                checkTicker.style.display = "none"
                resultTicker.classList.add("animate__animated", "animate__zoomIn")
                resultTicker.style.display = "block"
                removeButtonLoadingState()
            } else if (xhr.status != 200) {
                errorMessage.classList.add("animate__animated", "animate__fadeInDown")
                errorMessage.innerHTML = "Произошла ошибка при выполнении запроса или указан неверный тикер. Попробуйте снова."
                errorMessage.style.display = "block"
                removeButtonLoadingState()
            }
        };

        var data = JSON.stringify({
            fieldValue: inputField.value
        });
        xhr.send(data);
    }
}

function goBack() {
    checkTicker.style.display = "block"
    resultTicker.style.display = "none"
    tickerNameTitle.innerHTML = ""

}

function setTicker(element) {
    var inputElement = document.getElementById("tickerInput");
    inputElement.value = "";
    inputElement.value = element.innerText;
}

var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
})
