+++
authors = ["Issa Sanogo"]
title = "Support des Emojis"
date = "2023-07-07"
description = "Un guide d'utilisation des emojis avec Hugo"
tags = [
    "hugo",
    "markdown",
    "emoji",
]
categories = [
    "syntaxe",
    "démonstration du thème",
]
series = ["Démonstration du Thème"]
+++

Les emojis peuvent être activés dans un projet Hugo de plusieurs manières.

<!--more-->

La fonction [`emojify`](https://gohugo.io/functions/emojify/) peut être appelée directement dans les modèles ou avec des [Inline Shortcodes](https://gohugo.io/templates/shortcode-templates/#inline-shortcodes).

Pour activer les emojis de manière globale, appliquez `enableEmoji` avec la valeur `true` dans la [configuration](https://gohugo.io/getting-started/configuration/) de votre site, puis vous pourrez ajouter des codes emoji directement dans les fichiers de contenu. Par exemple :

<p><span class="nowrap"><span class="emojify">🙈</span> <code>:see_no_evil:</code></span>  <span class="nowrap"><span class="emojify">🙉</span> <code>:hear_no_evil:</code></span>  <span class="nowrap"><span class="emojify">🙊</span> <code>:speak_no_evil:</code></span></p>
<br>

Le [Emoji cheat sheet](http://www.emoji-cheat-sheet.com/) est une référence utile pour identifier les codes des emojis.

---

**Note :** Les étapes précédentes activent les caractères et séquences d'emoji du Standard Unicode dans Hugo, mais le rendu de ces glyphes dépend du navigateur et de la plateforme utilisée. Pour choisir le style des emojis, vous pouvez utiliser une police emoji tierce ou une liste de polices. Par exemple :

{{< highlight html >}}
.emoji {
font-family: Apple Color Emoji, Segoe UI Emoji, NotoColorEmoji, Segoe UI Symbol, Android Emoji, EmojiSymbols;
}
{{< /highlight >}}

{{< css.inline >}}

<style>
.emojify {
	font-family: Apple Color Emoji, Segoe UI Emoji, NotoColorEmoji, Segoe UI Symbol, Android Emoji, EmojiSymbols;
	font-size: 2rem;
	vertical-align: middle;
}
@media screen and (max-width:650px) {
  .nowrap {
    display: block;
    margin: 25px 0;
  }
}
</style>

{{< /css.inline >}}
