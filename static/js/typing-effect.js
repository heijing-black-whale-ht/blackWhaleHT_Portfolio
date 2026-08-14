function startTypingEffect(elementId, sentences, options = {}) {
    const el = document.getElementById(elementId);
    if (!el) return;

    const typeSpeed = options.typeSpeed || 60; // ms per character typed
    const eraseSpeed = options.eraseSpeed || 30; // ms per character erased
    const pauseAfterType = options.pauseAfterType || 1500; // pause when sentence is complete
    const pauseAfterErase = options.pauseAfterErase || 300; // pause before typing next sentence
    const loop = options.loop !== undefined ? options.loop : true;
    const onComplete = options.onComplete || null;

    let sentenceIndex = 0;
    let charIndex = 0;

    function typeNextChar() {
        const currentSentence = sentences[sentenceIndex];
        charIndex++;
        el.textContent = currentSentence.slice(0, charIndex);

        if (charIndex < currentSentence.length) {
            setTimeout(typeNextChar, typeSpeed);
        } else {
            const isLastSentence = sentenceIndex === sentences.length - 1;

            if (isLastSentence && !loop) {
                if (onComplete) setTimeout(onComplete, pauseAfterType);
                return;
            }
            setTimeout(eraseNextChar, pauseAfterType);
        }
    }

    function eraseNextChar() {
        charIndex--;
        el.textContent = sentences[sentenceIndex].slice(0, charIndex);

        if (charIndex > 0) {
            setTimeout(eraseNextChar, eraseSpeed);
        } else {
            sentenceIndex = (sentenceIndex + 1) % sentences.length;
            setTimeout(typeNextChar, pauseAfterErase);
        }
    }

    typeNextChar();
}