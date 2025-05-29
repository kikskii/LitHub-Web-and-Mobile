document.addEventListener('DOMContentLoaded', function() {
    // Get elements
    const carousel = document.querySelector('.carousel');
    const leftBtn = document.querySelector('.arrow-btn.left');
    const rightBtn = document.querySelector('.arrow-btn.right');
    
    // Debug log to check if elements are found
    console.log('Carousel:', carousel);
    console.log('Left Button:', leftBtn);
    console.log('Right Button:', rightBtn);
    
    // Calculate card width
    const cardWidth = carousel.querySelector('.card').offsetWidth + 16;
    console.log('Card Width:', cardWidth);

    // Add click event listeners
    leftBtn.onclick = function() {
        console.log('Left button clicked');
        carousel.scrollLeft -= cardWidth;
        console.log('New scroll position:', carousel.scrollLeft);
    };

    rightBtn.onclick = function() {
        console.log('Right button clicked');
        carousel.scrollLeft += cardWidth;
        console.log('New scroll position:', carousel.scrollright);
    };
});