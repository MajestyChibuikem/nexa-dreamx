// Simple and robust withdrawal functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Withdrawal page loaded');
    
    // Get elements
    const cryptoOptions = document.querySelectorAll('.crypto-option');
    const amountTypeBtns = document.querySelectorAll('.amount-type-btn');
    const amountInput = document.getElementById('id_amount');
    const amountSuffix = document.getElementById('amountSuffix');
    const cryptoEquivalent = document.getElementById('cryptoEquivalent');
    const quickAmountBtns = document.querySelectorAll('.quick-amount-btn');
    const pasteAddressBtn = document.getElementById('pasteAddressBtn');
    const destinationAddressInput = document.getElementById('id_destination_address');
    const cryptoTypeInput = document.getElementById('id_crypto_type');
    
    // Get data from template
    const availableCryptos = [];
    cryptoOptions.forEach(option => {
        availableCryptos.push({
            symbol: option.dataset.crypto,
            name: option.dataset.name,
            balance: parseFloat(option.dataset.balance),
            usd_value: parseFloat(option.dataset.usd_value),
            network: option.dataset.network
        });
    });
    
    // Selected crypto data
    let selectedCrypto = availableCryptos[0] || {
        symbol: 'BTC',
        name: 'Bitcoin',
        balance: 0.02,
        usd_value: 1000.00,
        network: 'Bitcoin Network'
    };
    
    let amountType = 'usd';
    const userBalance = parseFloat(document.querySelector('#maxAmount')?.textContent.replace('Max: $', '') || '1000.00');
    const minWithdrawal = parseFloat(document.querySelector('#minAmount')?.textContent.replace('Min: $', '') || '10.00');
    const networkFee = 0.0005;
    const processingFee = 1.00;
    
    console.log('Initialized with:', { selectedCrypto, userBalance, minWithdrawal });
    
    // Crypto selection
    cryptoOptions.forEach(option => {
        option.addEventListener('click', function() {
            console.log('Crypto selected:', this.dataset.crypto);
            
            // Remove selected class
            cryptoOptions.forEach(opt => opt.classList.remove('selected'));
            this.classList.add('selected');
            
            // Update selected crypto data
            selectedCrypto = {
                symbol: this.dataset.crypto,
                name: this.dataset.name,
                balance: parseFloat(this.dataset.balance),
                usd_value: parseFloat(this.dataset.usd_value),
                network: this.dataset.network
            };
            
            // Update display
            updateCryptoDisplay();
            updateCryptoEquivalent();
            updateSummary();
        });
    });
    
    // Amount type toggle
    amountTypeBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            console.log('Amount type changed to:', this.dataset.type);
            
            amountTypeBtns.forEach(b => {
                b.classList.remove('active', 'bg-blue-600', 'text-white');
                b.classList.add('bg-gray-700', 'text-gray-300');
            });
            this.classList.add('active', 'bg-blue-600', 'text-white');
            this.classList.remove('bg-gray-700', 'text-gray-300');
            
            amountType = this.dataset.type;
            amountSuffix.textContent = amountType.toUpperCase();
            
            // Convert amount if there's a value
            const currentAmount = parseFloat(amountInput.value) || 0;
            if (currentAmount > 0) {
                if (amountType === 'crypto') {
                    const cryptoAmount = (currentAmount / selectedCrypto.usd_value) * selectedCrypto.balance;
                    amountInput.value = cryptoAmount.toFixed(8);
                } else {
                    const usdAmount = (currentAmount / selectedCrypto.balance) * selectedCrypto.usd_value;
                    amountInput.value = usdAmount.toFixed(2);
                }
                updateCryptoEquivalent();
                updateSummary();
            }
        });
    });
    
    // Amount input changes
    if (amountInput) {
        amountInput.addEventListener('input', function() {
            updateCryptoEquivalent();
            updateSummary();
            validateAmount();
        });
    }
    
    // Quick amount buttons
    quickAmountBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const percent = parseFloat(this.dataset.percent);
            console.log('Quick amount clicked:', percent + '%');
            
            let amount;
            
            if (amountType === 'usd') {
                amount = (userBalance * percent / 100).toFixed(2);
            } else {
                amount = (selectedCrypto.balance * percent / 100).toFixed(8);
            }
            
            amountInput.value = amount;
            updateCryptoEquivalent();
            updateSummary();
            validateAmount();
        });
    });
    
    // Paste address button
    if (pasteAddressBtn && destinationAddressInput) {
        pasteAddressBtn.addEventListener('click', function() {
            console.log('Paste address clicked');
            navigator.clipboard.readText().then(text => {
                destinationAddressInput.value = text;
            }).catch(err => {
                console.error('Failed to read clipboard:', err);
            });
        });
    }
    
    // Update crypto display
    function updateCryptoDisplay() {
        const icon = document.getElementById('selectedCryptoIcon');
        const name = document.getElementById('selectedCryptoName');
        const network = document.getElementById('selectedCryptoNetwork');
        const balance = document.getElementById('selectedCryptoBalance');
        
        if (icon) {
            icon.textContent = selectedCrypto.symbol;
            icon.className = `crypto-icon ${selectedCrypto.symbol.toLowerCase()}`;
        }
        if (name) name.textContent = `${selectedCrypto.name} (${selectedCrypto.symbol})`;
        if (network) network.textContent = selectedCrypto.network;
        if (balance) balance.textContent = `Balance: ${selectedCrypto.balance.toFixed(8)} ${selectedCrypto.symbol}`;
        
        // Update hidden input
        if (cryptoTypeInput) cryptoTypeInput.value = selectedCrypto.symbol;
    }
    
    // Update crypto equivalent
    function updateCryptoEquivalent() {
        if (!amountInput || !cryptoEquivalent) return;
        
        const amount = parseFloat(amountInput.value) || 0;
        let cryptoAmount = amount;
        
        if (amountType === 'usd') {
            cryptoAmount = (amount / selectedCrypto.usd_value) * selectedCrypto.balance;
        }
        
        cryptoEquivalent.innerHTML = `<span class="text-blue-400 font-mono">≈ ${cryptoAmount.toFixed(8)} ${selectedCrypto.symbol}</span>`;
    }
    
    // Update summary
    function updateSummary() {
        if (!amountInput) return;
        
        const amount = parseFloat(amountInput.value) || 0;
        let usdAmount = amount;
        
        if (amountType === 'crypto') {
            usdAmount = (amount / selectedCrypto.balance) * selectedCrypto.usd_value;
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
    
    // Validate amount
    function validateAmount() {
        if (!amountInput) return;
        
        const amount = parseFloat(amountInput.value) || 0;
        let isValid = true;
        let errorMessage = '';
        
        if (amountType === 'usd') {
            if (amount < minWithdrawal) {
                isValid = false;
                errorMessage = `Minimum withdrawal is $${minWithdrawal.toFixed(2)}`;
            } else if (amount > userBalance) {
                isValid = false;
                errorMessage = `Amount exceeds available balance of $${userBalance.toFixed(2)}`;
            }
        } else {
            const usdAmount = (amount / selectedCrypto.balance) * selectedCrypto.usd_value;
            if (usdAmount < minWithdrawal) {
                isValid = false;
                errorMessage = `Minimum withdrawal is $${minWithdrawal.toFixed(2)}`;
            } else if (usdAmount > userBalance) {
                isValid = false;
                errorMessage = `Amount exceeds available balance of $${userBalance.toFixed(2)}`;
            }
        }
        
        if (isValid) {
            amountInput.setCustomValidity('');
        } else {
            amountInput.setCustomValidity(errorMessage);
        }
    }
    
    // Form submission
    const form = document.getElementById('withdrawalForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Form submitted');
            const withdrawBtn = document.getElementById('withdrawBtn');
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
    
    // Initialize
    updateCryptoDisplay();
    updateCryptoEquivalent();
    updateSummary();
    console.log('Withdrawal page initialized successfully');
});