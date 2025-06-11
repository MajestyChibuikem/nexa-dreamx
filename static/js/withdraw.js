// In static/js/withdrawals.js
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('withdrawalForm');
    const amountInput = document.getElementById('id_amount');
    const withdrawBtn = document.getElementById('withdrawBtn');
    const availableBalance = parseFloat("{{ user.wallet_set.get.wallet_type='INTEREST'.available_balance }}");
    
    // Real-time validation
    amountInput.addEventListener('input', function() {
        const amount = parseFloat(this.value) || 0;
        const minAmount = parseFloat("{{ min_withdrawal_amount }}");
        
        if (amount > availableBalance) {
            this.setCustomValidity(`Amount exceeds available balance of $${availableBalance.toFixed(2)}`);
            withdrawBtn.disabled = true;
        } else if (amount < minAmount) {
            this.setCustomValidity(`Minimum withdrawal is $${minAmount.toFixed(2)}`);
            withdrawBtn.disabled = true;
        } else {
            this.setCustomValidity('');
            withdrawBtn.disabled = false;
        }
        
        // Update summary
        updateSummary(amount);
    });
    
    function updateSummary(amount) {
        const networkFee = parseFloat("{{ network_fee }}");
        const processingFee = parseFloat("{{ processing_fee }}");
        const totalDeducted = amount + networkFee + processingFee;
        const willReceive = amount - processingFee;
        
        document.getElementById('summaryAmount').textContent = `$${amount.toFixed(2)}`;
        document.getElementById('summaryTotal').textContent = `$${totalDeducted.toFixed(2)}`;
        document.getElementById('summaryReceive').textContent = `$${willReceive.toFixed(2)}`;
    }
    
    // Quick amount buttons
    document.querySelectorAll('.quick-amount-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const percent = parseFloat(this.dataset.percent);
            const amount = (availableBalance * percent / 100).toFixed(2);
            amountInput.value = amount;
            amountInput.dispatchEvent(new Event('input'));
        });
    });
});