# nice-backend

> a server for distributed search of square-cube pandigitals 

## Why does this exist

Square-cube pandigials ("nice" numbers) seem to be distributed pseudo-randomly. It doesn't take very long to check if a number is pandigital in a specific base, but even after we narrow the search range to numbers with the right amount of digits in their square and cube there's a lot of numbers to check. Even worse, it doesn't seem like there are any nice numbers between bases 10 and 140-ish, and it would take an impossibly long time to exhaustively search those at the higher end where the metaphorical ground is more fertile.

Here we have two tricks: data and [dakka](https://tvtropes.org/pmwiki/pmwiki.php/Main/MoreDakka). With enough data on the "niceness" of many numbers, we may be able to find patterns in (or at least take guesses about) which regions are more likely to have nice numbers. Then once we have some tricks, we can start checking semi-randomly in the bases likely to have 100% nice numbers. With enough ~~dakka~~ processing time and luck, anything is possible!

For more background, check out the [original article](https://beautifulthorns.wixsite.com/home/post/is-69-unique) and [my findings](https://wasabipesto.com/nice).

## Where's the client?

You can find the python client here: [nice-client](https://github.com/wasabipesto/nice-client)