// In static/js/withdrawals.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('Withdrawal form JavaScript loaded');
    
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
    
    // Check if elements exist
    if (!form) {
        console.error('Form not found');
        return;
    }
    
    if (!amountInput) {
        console.error('Amount input not found');
        return;
    }
    
    // Get context data from template with error handling
    let availableCryptos = [];
    let minWithdrawalAmount = 10.00;
    let networkFee = 0.0005;
    let processingFee = 1.00;
    let userBalance = 0.00;
    
    try {
        const availableCryptosElement = document.getElementById('availableCryptosData');
        if (availableCryptosElement) {
            availableCryptos = JSON.parse(availableCryptosElement.textContent);
        }
        
        const minWithdrawalElement = document.getElementById('minWithdrawalAmount');
        if (minWithdrawalElement) {
            minWithdrawalAmount = parseFloat(minWithdrawalElement.textContent);
        }
        
        const networkFeeElement = document.getElementById('networkFee');
        if (networkFeeElement) {
            networkFee = parseFloat(networkFeeElement.textContent);
        }
        
        const processingFeeElement = document.getElementById('processingFee');
        if (processingFeeElement) {
            processingFee = parseFloat(processingFeeElement.textContent);
        }
        
        const userBalanceElement = document.getElementById('userBalance');
        if (userBalanceElement) {
            userBalance = parseFloat(userBalanceElement.textContent);
        }
    } catch (error) {
        console.error('Error parsing template data:', error);
    }
    
    console.log('Available cryptos:', availableCryptos);
    console.log('User balance:', userBalance);
    
    let selectedCrypto = availableCryptos.length > 0 ? availableCryptos[0] : null;
    let amountType = 'usd'; // 'usd' or 'crypto'
    
    // Initialize the form
    function initializeForm() {
        if (selectedCrypto) {
            updateSelectedCrypto(selectedCrypto);
        }
        updateAmountValidation();
        updateSummary();
        updateCryptoEquivalent();
    }
    
    // Handle crypto selection
    if (cryptoOptions.length > 0) {
        cryptoOptions.forEach(option => {
            option.addEventListener('click', function() {
                console.log('Crypto option clicked:', this.dataset.crypto);
                
                // Remove selected class from all options
                cryptoOptions.forEach(opt => opt.classList.remove('selected'));
                // Add selected class to clicked option
                this.classList.add('selected');
                
                // Get crypto data
                const cryptoSymbol = this.dataset.crypto;
                selectedCrypto = availableCryptos.find(crypto => crypto.symbol === cryptoSymbol);
                
                if (selectedCrypto) {
                    // Update form
                    updateSelectedCrypto(selectedCrypto);
                    updateAmountValidation();
                    updateSummary();
                    updateCryptoEquivalent();
                }
            });
        });
    }
    
    // Update selected crypto display
    function updateSelectedCrypto(crypto) {
        if (!crypto) return;
        
        if (selectedCryptoIcon) {
            selectedCryptoIcon.textContent = crypto.symbol;
            selectedCryptoIcon.className = `crypto-icon ${crypto.symbol.toLowerCase()}`;
        }
        
        if (selectedCryptoName) {
            selectedCryptoName.textContent = `${crypto.name} (${crypto.symbol})`;
        }
        
        if (selectedCryptoNetwork) {
            selectedCryptoNetwork.textContent = crypto.network;
        }
        
        if (selectedCryptoBalance) {
            selectedCryptoBalance.textContent = `Balance: ${parseFloat(crypto.balance).toFixed(8)} ${crypto.symbol}`;
        }
        
        // Update hidden input
        if (cryptoTypeInput) {
            cryptoTypeInput.value = crypto.symbol;
        }
    }
    
    // Handle amount type toggle (USD/Crypto)
    if (amountTypeBtns.length > 0) {
        amountTypeBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                console.log('Amount type button clicked:', this.dataset.type);
                
                amountTypeBtns.forEach(b => {
                    b.classList.remove('active', 'bg-blue-600', 'text-white');
                    b.classList.add('bg-gray-700', 'text-gray-300');
                });
                this.classList.add('active', 'bg-blue-600', 'text-white');
                this.classList.remove('bg-gray-700', 'text-gray-300');
                
                amountType = this.dataset.type;
                
                if (amountSuffix) {
                    amountSuffix.textContent = amountType.toUpperCase();
                }
                
                // Convert amount if needed
                const currentAmount = parseFloat(amountInput.value) || 0;
                if (currentAmount > 0 && selectedCrypto) {
                    if (amountType === 'crypto') {
                        // Convert USD to crypto
                        const cryptoAmount = currentAmount / parseFloat(selectedCrypto.usd_value) * parseFloat(selectedCrypto.balance);
                        amountInput.value = cryptoAmount.toFixed(8);
                    } else {
                        // Convert crypto to USD
                        const usdAmount = currentAmount / parseFloat(selectedCrypto.balance) * parseFloat(selectedCrypto.usd_value);
                        amountInput.value = usdAmount.toFixed(2);
                    }
                    updateAmountValidation();
                    updateSummary();
                    updateCryptoEquivalent();
                }
            });
        });
    }
    
    // Handle amount input changes
    if (amountInput) {
        amountInput.addEventListener('input', function() {
            updateAmountValidation();
            updateSummary();
            updateCryptoEquivalent();
        });
    }
    
    // Update amount validation
    function updateAmountValidation() {
        if (!amountInput) return;
        
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
            if (selectedCrypto) {
                const usdAmount = amount / parseFloat(selectedCrypto.balance) * parseFloat(selectedCrypto.usd_value);
                if (usdAmount < minWithdrawalAmount) {
                    isValid = false;
                    errorMessage = `Minimum withdrawal is $${minWithdrawalAmount.toFixed(2)}`;
                } else if (usdAmount > userBalance) {
                    isValid = false;
                    errorMessage = `Amount exceeds available balance of $${userBalance.toFixed(2)}`;
                }
            }
        }
        
        if (isValid) {
            amountInput.setCustomValidity('');
            if (withdrawBtn) withdrawBtn.disabled = false;
        } else {
            amountInput.setCustomValidity(errorMessage);
            if (withdrawBtn) withdrawBtn.disabled = true;
        }
    }
    
    // Update summary calculations
    function updateSummary() {
        if (!amountInput) return;
        
        const amount = parseFloat(amountInput.value) || 0;
        let usdAmount = amount;
        
        if (amountType === 'crypto' && selectedCrypto) {
            usdAmount = amount / parseFloat(selectedCrypto.balance) * parseFloat(selectedCrypto.usd_value);
        }
        
        const totalDeducted = usdAmount + networkFee + processingFee;
        const willReceive = usdAmount - processingFee;
        
        const summaryAmount = document.getElementById('summaryAmount');
        const summaryTotal = document.getElementById('summaryTotal');
        const summaryReceive = document.getElementById('summaryReceive');
        
        if (summaryAmount) summaryAmount.textContent = `$${usdAmount.toFixed(2)}`;
        if (summaryTotal) summaryTotal.textContent = `$${totalDeducted.toFixed(2)}`;
        if (summaryReceive) summaryReceive.textContent = `$${willReceive.toFixed(2)}`;
    }
    
    // Update crypto equivalent display
    function updateCryptoEquivalent() {
        if (!amountInput || !cryptoEquivalent || !selectedCrypto) return;
        
        const amount = parseFloat(amountInput.value) || 0;
        let cryptoAmount = amount;
        
        if (amountType === 'usd') {
            cryptoAmount = amount / parseFloat(selectedCrypto.usd_value) * parseFloat(selectedCrypto.balance);
        }
        
        cryptoEquivalent.innerHTML = `<span class="text-blue-400 font-mono">≈ ${cryptoAmount.toFixed(8)} ${selectedCrypto.symbol}</span>`;
    }
    
    // Handle quick amount buttons
    if (quickAmountBtns.length > 0) {
        quickAmountBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const percent = parseFloat(this.dataset.percent);
                console.log('Quick amount button clicked:', percent + '%');
                
                let amount;
                
                if (amountType === 'usd') {
                    amount = (userBalance * percent / 100).toFixed(2);
                } else {
                    if (selectedCrypto) {
                        amount = (parseFloat(selectedCrypto.balance) * percent / 100).toFixed(8);
                    } else {
                        amount = '0.00000000';
                    }
                }
                
                if (amountInput) {
                    amountInput.value = amount;
                    updateAmountValidation();
                    updateSummary();
                    updateCryptoEquivalent();
                }
            });
        });
    }
    
    // Handle paste address button
    if (pasteAddressBtn && destinationAddressInput) {
        pasteAddressBtn.addEventListener('click', function() {
            console.log('Paste address button clicked');
            navigator.clipboard.readText().then(text => {
                destinationAddressInput.value = text;
            }).catch(err => {
                console.error('Failed to read clipboard: ', err);
            });
        });
    }
    
    // Form submission
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Form submission started');
            
            if (!form.checkValidity()) {
                e.preventDefault();
                console.log('Form validation failed');
                return false;
            }
            
            // Show loading state
            if (withdrawBtn) {
                withdrawBtn.disabled = true;
                withdrawBtn.innerHTML = `
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Processing...
                `;
            }
        });
    }
    
    // Initialize the form
    initializeForm();
    console.log('Withdrawal form initialization complete');
});