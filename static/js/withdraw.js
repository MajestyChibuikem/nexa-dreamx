// In static/js/withdrawals.js
document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const form = document.getElementById('withdrawalForm');
    const amountInput = document.getElementById('id_amount');
    const withdrawBtn = document.getElementById('withdrawBtn');
    const cryptoOptions = document.querySelectorAll('.crypto-option');
    const selectedCryptoIcon = document.getElementById('selectedCryptoIcon');
    const selectedCryptoName = document.getElementById('selectedCryptoName');
    const selectedCryptoNetwork = document.getElementById('selectedCryptoNetwork');
    const selectedCryptoBalance = document.getElementById('selectedCryptoBalance');
    const cryptoTypeInput = document.getElementById('id_crypto_type');
    const amountTypeBtns = document.querySelectorAll('.amount-type-btn');
    const amountSuffix = document.getElementById('amountSuffix');
    const cryptoEquivalent = document.getElementById('cryptoEquivalent');
    const quickAmountBtns = document.querySelectorAll('.quick-amount-btn');
    const pasteAddressBtn = document.getElementById('pasteAddressBtn');
    const destinationAddressInput = document.getElementById('id_destination_address');
    
    // Get context data from template
    const availableCryptos = JSON.parse(document.getElementById('availableCryptosData').textContent);
    const minWithdrawalAmount = parseFloat(document.getElementById('minWithdrawalAmount').textContent);
    const networkFee = parseFloat(document.getElementById('networkFee').textContent);
    const processingFee = parseFloat(document.getElementById('processingFee').textContent);
    const userBalance = parseFloat(document.getElementById('userBalance').textContent);
    
    let selectedCrypto = availableCryptos[0];
    let amountType = 'usd'; // 'usd' or 'crypto'
    
    // Initialize the form
    function initializeForm() {
        updateSelectedCrypto(selectedCrypto);
        updateAmountValidation();
        updateSummary();
    }
    
    // Handle crypto selection
    cryptoOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Remove selected class from all options
            cryptoOptions.forEach(opt => opt.classList.remove('selected'));
            // Add selected class to clicked option
            this.classList.add('selected');
            
            // Get crypto data
            const cryptoSymbol = this.dataset.crypto;
            selectedCrypto = availableCryptos.find(crypto => crypto.symbol === cryptoSymbol);
            
            // Update form
            updateSelectedCrypto(selectedCrypto);
            updateAmountValidation();
            updateSummary();
        });
    });
    
    // Update selected crypto display
    function updateSelectedCrypto(crypto) {
        selectedCryptoIcon.textContent = crypto.symbol;
        selectedCryptoIcon.className = `crypto-icon ${crypto.symbol.toLowerCase()}`;
        selectedCryptoName.textContent = `${crypto.name} (${crypto.symbol})`;
        selectedCryptoNetwork.textContent = crypto.network;
        selectedCryptoBalance.textContent = `Balance: ${crypto.balance.toFixed(8)} ${crypto.symbol}`;
        
        // Update hidden input
        cryptoTypeInput.value = crypto.symbol;
    }
    
    // Handle amount type toggle (USD/Crypto)
    amountTypeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            amountTypeBtns.forEach(b => {
                b.classList.remove('active', 'bg-blue-600', 'text-white');
                b.classList.add('bg-gray-700', 'text-gray-300');
            });
            this.classList.add('active', 'bg-blue-600', 'text-white');
            this.classList.remove('bg-gray-700', 'text-gray-300');
            
            amountType = this.dataset.type;
            amountSuffix.textContent = amountType.toUpperCase();
            
            // Convert amount if needed
            const currentAmount = parseFloat(amountInput.value) || 0;
            if (currentAmount > 0) {
                if (amountType === 'crypto') {
                    // Convert USD to crypto
                    const cryptoAmount = currentAmount / selectedCrypto.usd_value * selectedCrypto.balance;
                    amountInput.value = cryptoAmount.toFixed(8);
                } else {
                    // Convert crypto to USD
                    const usdAmount = currentAmount / selectedCrypto.balance * selectedCrypto.usd_value;
                    amountInput.value = usdAmount.toFixed(2);
                }
                updateAmountValidation();
                updateSummary();
            }
        });
    });
    
    // Handle amount input changes
    amountInput.addEventListener('input', function() {
        updateAmountValidation();
        updateSummary();
        updateCryptoEquivalent();
    });
    
    // Update amount validation
    function updateAmountValidation() {
        const amount = parseFloat(amountInput.value) || 0;
        let isValid = true;
        let errorMessage = '';
        
        if (amountType === 'usd') {
            if (amount < minWithdrawalAmount) {
                isValid = false;
                errorMessage = `Minimum withdrawal is $${minWithdrawalAmount.toFixed(2)}`;
            } else if (amount > userBalance) {
                isValid = false;
                errorMessage = `Amount exceeds available balance of $${userBalance.toFixed(2)}`;
            }
        } else {
            const usdAmount = amount / selectedCrypto.balance * selectedCrypto.usd_value;
            if (usdAmount < minWithdrawalAmount) {
                isValid = false;
                errorMessage = `Minimum withdrawal is $${minWithdrawalAmount.toFixed(2)}`;
            } else if (usdAmount > userBalance) {
                isValid = false;
                errorMessage = `Amount exceeds available balance of $${userBalance.toFixed(2)}`;
            }
        }
        
        if (isValid) {
            amountInput.setCustomValidity('');
            withdrawBtn.disabled = false;
        } else {
            amountInput.setCustomValidity(errorMessage);
            withdrawBtn.disabled = true;
        }
    }
    
    // Update summary calculations
    function updateSummary() {
        const amount = parseFloat(amountInput.value) || 0;
        let usdAmount = amount;
        
        if (amountType === 'crypto') {
            usdAmount = amount / selectedCrypto.balance * selectedCrypto.usd_value;
        }
        
        const totalDeducted = usdAmount + networkFee + processingFee;
        const willReceive = usdAmount - processingFee;
        
        document.getElementById('summaryAmount').textContent = `$${usdAmount.toFixed(2)}`;
        document.getElementById('summaryTotal').textContent = `$${totalDeducted.toFixed(2)}`;
        document.getElementById('summaryReceive').textContent = `$${willReceive.toFixed(2)}`;
    }
    
    // Update crypto equivalent display
    function updateCryptoEquivalent() {
        const amount = parseFloat(amountInput.value) || 0;
        let cryptoAmount = amount;
        
        if (amountType === 'usd') {
            cryptoAmount = amount / selectedCrypto.usd_value * selectedCrypto.balance;
        }
        
        cryptoEquivalent.innerHTML = `<span class="text-blue-400 font-mono">≈ ${cryptoAmount.toFixed(8)} ${selectedCrypto.symbol}</span>`;
    }
    
    // Handle quick amount buttons
    quickAmountBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const percent = parseFloat(this.dataset.percent);
            let amount;
            
            if (amountType === 'usd') {
                amount = (userBalance * percent / 100).toFixed(2);
            } else {
                amount = (selectedCrypto.balance * percent / 100).toFixed(8);
            }
            
            amountInput.value = amount;
            updateAmountValidation();
            updateSummary();
            updateCryptoEquivalent();
        });
    });
    
    // Handle paste address button
    pasteAddressBtn.addEventListener('click', function() {
        navigator.clipboard.readText().then(text => {
            destinationAddressInput.value = text;
        }).catch(err => {
            console.error('Failed to read clipboard: ', err);
        });
    });
    
    // Form submission
    form.addEventListener('submit', function(e) {
        if (!form.checkValidity()) {
            e.preventDefault();
            return false;
        }
        
        // Show loading state
        withdrawBtn.disabled = true;
        withdrawBtn.innerHTML = `
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Processing...
        `;
    });
    
    // Initialize the form
    initializeForm();
});