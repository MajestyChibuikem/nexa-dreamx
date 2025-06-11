document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const cryptoOptions = document.querySelectorAll('.crypto-option');
    const selectedCryptoIcon = document.getElementById('selectedCryptoIcon');
    const selectedCryptoName = document.getElementById('selectedCryptoName');
    const selectedCryptoNetwork = document.getElementById('selectedCryptoNetwork');
    const selectedCryptoBalance = document.getElementById('selectedCryptoBalance');
    const amountInput = document.querySelector('input[name="amount"]');
    const amountTypeButtons = document.querySelectorAll('.amount-type-btn');
    const quickAmountButtons = document.querySelectorAll('.quick-amount-btn');
    const cryptoEquivalent = document.getElementById('cryptoEquivalent');
    const summaryAmount = document.getElementById('summaryAmount');
    const summaryTotal = document.getElementById('summaryTotal');
    const summaryReceive = document.getElementById('summaryReceive');
    const pasteAddressBtn = document.getElementById('pasteAddressBtn');
    const destinationAddress = document.querySelector('input[name="destination_address"]');
    const confirmationCheckbox = document.querySelector('input[name="confirmation"]');
    const withdrawBtn = document.getElementById('withdrawBtn');
    const refreshBalanceBtn = document.getElementById('refreshBalance');

    // Constants from template variables
    const NETWORK_FEE = parseFloat('{{ network_fee }}');
    const PROCESSING_FEE = parseFloat('{{ processing_fee }}');
    const MIN_WITHDRAWAL = parseFloat('{{ min_withdrawal_amount }}');
    const MAX_WITHDRAWAL = parseFloat('{{ user.account.total_balance }}');

    // State
    let currentCrypto = {
        symbol: '{{ available_cryptos.0.symbol }}',
        name: '{{ available_cryptos.0.name }}',
        network: '{{ available_cryptos.0.network }}',
        balance: parseFloat('{{ available_cryptos.0.balance }}'),
        usd_value: parseFloat('{{ available_cryptos.0.usd_value }}'),
        price: parseFloat('{{ available_cryptos.0.usd_value }}') / parseFloat('{{ available_cryptos.0.balance }}')
    };
    let isUSDInput = true;

    // Initialize
    updateNetworkDropdown();
    updateFeeSummary();
    setupEventListeners();

    // Functions
    function setupEventListeners() {
        // Crypto selection
        cryptoOptions.forEach(option => {
            option.addEventListener('click', function() {
                const symbol = this.dataset.crypto;
                selectCrypto(symbol);
            });
        });

        // Amount type toggle (USD/Crypto)
        amountTypeButtons.forEach(button => {
            button.addEventListener('click', function() {
                amountTypeButtons.forEach(btn => btn.classList.remove('active', 'bg-blue-600', 'text-white'));
                amountTypeButtons.forEach(btn => btn.classList.add('bg-gray-700', 'text-gray-300'));
                
                this.classList.add('active', 'bg-blue-600', 'text-white');
                this.classList.remove('bg-gray-700', 'text-gray-300');
                
                isUSDInput = this.dataset.type === 'usd';
                updateAmountSuffix();
                convertAmount();
            });
        });

        // Quick amount buttons
        quickAmountButtons.forEach(button => {
            button.addEventListener('click', function() {
                const percent = parseFloat(this.dataset.percent) / 100;
                let maxAmount = isUSDInput ? currentCrypto.usd_value : currentCrypto.balance;
                let amount = maxAmount * percent;
                
                amountInput.value = amount.toFixed(isUSDInput ? 2 : 8);
                convertAmount();
                updateFeeSummary();
            });
        });

        // Amount input changes
        amountInput.addEventListener('input', function() {
            convertAmount();
            updateFeeSummary();
        });

        // Paste address button
        pasteAddressBtn.addEventListener('click', async function() {
            try {
                const text = await navigator.clipboard.readText();
                destinationAddress.value = text;
            } catch (err) {
                console.error('Failed to read clipboard:', err);
                // Fallback for browsers without Clipboard API
                destinationAddress.value = prompt('Paste your wallet address:');
            }
        });

        // Form submission
        withdrawBtn.addEventListener('click', function(e) {
            if (!validateForm()) {
                e.preventDefault();
            }
        });

        // Balance refresh
        refreshBalanceBtn.addEventListener('click', function() {
            // This would typically be an AJAX call in a real implementation
            location.reload();
        });
    }

    function selectCrypto(symbol) {
        // Find the selected crypto from available_cryptos (simulated here)
        const cryptoElement = document.querySelector(`.crypto-option[data-crypto="${symbol}"]`);
        const cryptoData = {
            symbol: symbol,
            name: cryptoElement.querySelector('h4').textContent,
            network: cryptoElement.querySelector('p:nth-of-type(1)').textContent.split(' ')[0],
            balance: parseFloat(cryptoElement.querySelector('p:nth-of-type(2)').textContent.split(' ')[0]),
            usd_value: parseFloat(cryptoElement.querySelector('p:nth-of-type(3)').textContent.replace('$', ''))
        };
        
        cryptoData.price = cryptoData.usd_value / cryptoData.balance;
        currentCrypto = cryptoData;

        // Update UI
        cryptoOptions.forEach(opt => opt.classList.remove('selected'));
        cryptoElement.classList.add('selected');
        
        selectedCryptoIcon.textContent = cryptoData.symbol;
        selectedCryptoIcon.className = `crypto-icon ${getCryptoIconClass(cryptoData.symbol)}`;
        selectedCryptoName.textContent = `${cryptoData.name} (${cryptoData.symbol})`;
        selectedCryptoNetwork.textContent = cryptoData.network;
        selectedCryptoBalance.textContent = `Balance: ${cryptoData.balance.toFixed(8)} ${cryptoData.symbol}`;

        // Update network dropdown
        updateNetworkDropdown();
        
        // Reset and recalculate amounts
        amountInput.value = '';
        convertAmount();
        updateFeeSummary();
    }

    function getCryptoIconClass(symbol) {
        switch(symbol) {
            case 'ETH': return 'eth';
            case 'USDT': return 'usdt';
            case 'USD': return 'usd';
            default: return '';
        }
    }

    function updateNetworkDropdown() {
        const networkSelect = document.querySelector('select[name="network"]');
        // In a real app, this would come from the backend based on selected crypto
        networkSelect.value = currentCrypto.network;
    }

    function updateAmountSuffix() {
        const suffix = document.getElementById('amountSuffix');
        suffix.textContent = isUSDInput ? 'USD' : currentCrypto.symbol;
    }

    function convertAmount() {
        if (!amountInput.value) {
            cryptoEquivalent.innerHTML = `<span class="text-blue-400 font-mono">≈ 0.00000000 ${currentCrypto.symbol}</span>`;
            return;
        }

        const amount = parseFloat(amountInput.value);
        if (isNaN(amount)) {
            return;
        }

        if (isUSDInput) {
            const cryptoAmount = amount / currentCrypto.price;
            cryptoEquivalent.innerHTML = `<span class="text-blue-400 font-mono">≈ ${cryptoAmount.toFixed(8)} ${currentCrypto.symbol}</span>`;
        } else {
            const usdAmount = amount * currentCrypto.price;
            cryptoEquivalent.innerHTML = `<span class="text-blue-400 font-mono">≈ $${usdAmount.toFixed(2)}</span>`;
        }
    }

    function updateFeeSummary() {
        if (!amountInput.value) {
            summaryAmount.textContent = '$0.00';
            summaryTotal.textContent = '$0.00';
            summaryReceive.textContent = '$0.00';
            return;
        }

        const amount = parseFloat(amountInput.value);
        if (isNaN(amount)) return;

        // Convert to USD if input was in crypto
        const usdAmount = isUSDInput ? amount : amount * currentCrypto.price;

        const totalFees = NETWORK_FEE + PROCESSING_FEE;
        const totalDeducted = usdAmount + totalFees;
        const amountReceived = usdAmount - totalFees;

        summaryAmount.textContent = `$${usdAmount.toFixed(2)}`;
        summaryTotal.textContent = `$${totalDeducted.toFixed(2)}`;
        summaryReceive.textContent = `$${Math.max(0, amountReceived).toFixed(2)}`;
    }

    function validateForm() {
        let isValid = true;

        // Validate amount
        const amount = parseFloat(amountInput.value);
        if (isNaN(amount) || amount <= 0) {
            isValid = false;
            showError(amountInput, 'Please enter a valid amount');
        } else {
            const usdAmount = isUSDInput ? amount : amount * currentCrypto.price;
            if (usdAmount < MIN_WITHDRAWAL) {
                isValid = false;
                showError(amountInput, `Minimum withdrawal is $${MIN_WITHDRAWAL}`);
            }
            if (usdAmount > currentCrypto.usd_value) {
                isValid = false;
                showError(amountInput, `Amount exceeds your available balance`);
            }
        }

        // Validate destination address
        if (!destinationAddress.value.trim()) {
            isValid = false;
            showError(destinationAddress, 'Wallet address is required');
        }

        // Validate confirmation
        if (!confirmationCheckbox.checked) {
            isValid = false;
            showError(confirmationCheckbox, 'You must confirm the withdrawal');
        }

        return isValid;
    }

    function showError(element, message) {
        // In a real implementation, you'd show this near the element
        alert(message);
        element.focus();
    }
});