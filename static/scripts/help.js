/**
 * Priority Care - Help Page JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize FAQ accordion
    initializeFAQ();
});

/**
 * Initialize FAQ accordion functionality
 */
function initializeFAQ() {
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            toggleFaq(this);
        });
    });
}

/**
 * Toggle FAQ item - can be called from HTML onclick or event listener
 */
function toggleFaq(button) {
    const faqItem = button.closest('.faq-item');
    
    if (!faqItem) {
        console.error('FAQ item not found');
        return;
    }
    
    const isOpen = faqItem.classList.contains('open');
    
    // Close all FAQ items first
    const allFaqItems = document.querySelectorAll('.faq-item');
    allFaqItems.forEach(item => {
        item.classList.remove('open');
        const answer = item.querySelector('.faq-answer');
        if (answer) {
            answer.style.maxHeight = '0';
        }
    });
    
    // Toggle current item (open if it was closed)
    if (!isOpen) {
        faqItem.classList.add('open');
        const answer = faqItem.querySelector('.faq-answer');
        if (answer) {
            // Set max-height to scrollHeight for smooth animation
            answer.style.maxHeight = answer.scrollHeight + 'px';
        }
    }
}

/**
 * Search FAQ content (future enhancement)
 */
function searchFAQ(searchTerm) {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question span').textContent.toLowerCase();
        const answer = item.querySelector('.faq-answer').textContent.toLowerCase();
        
        if (question.includes(searchTerm.toLowerCase()) || 
            answer.includes(searchTerm.toLowerCase())) {
            item.style.display = '';
        } else {
            item.style.display = 'none';
        }
    });
}
