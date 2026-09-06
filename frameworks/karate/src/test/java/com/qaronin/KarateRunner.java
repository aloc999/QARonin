package com.qaronin;

import com.intuit.karate.junit5.Karate;

public class KarateRunner {
    @Karate.Test
    Karate runAll() {
        return Karate.run("classpath:features").relativeTo(getClass());
    }
}
