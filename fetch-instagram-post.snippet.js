(() => {
	let i = 0;

	const fetchNextSlide = () => {
		const nextSlideButton = document.querySelector('button[aria-label="Next"]');

		if (i > 0 || nextSlideButton === null) {
			const currentSlide = document.querySelector(`.html-div div[role="presentation"] ul > li:nth-child(${i > 1 ? 3 : 2}) img`);

			if (currentSlide !== undefined) {
				console.log(`Slide ${i > 0 ? i : 1}: ${currentSlide.src}`);
			} else {
				throw new Error(`Could not locate ${i > 0 ? i : 1}. slide!`);
			}
		}

		if (nextSlideButton !== null) {
			i++;

			nextSlideButton.click();
			window.setTimeout(fetchNextSlide, 500);
		}
	};

	fetchNextSlide();
})();
