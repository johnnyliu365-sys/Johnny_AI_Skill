package reusable.offlinegeo

private object TestAddressKeyPolicy : AddressKeyPolicy {
    override fun normalize(rawKey: RawAddressKey): NormalizedAddressKey? {
        val compactValue = rawKey.value.trim().lowercase().replace(Regex("\\s+"), " ")
        return compactValue.takeIf { it.isNotEmpty() }?.let(::NormalizedAddressKey)
    }

    override fun relaxedKey(normalizedKey: NormalizedAddressKey): RelaxedAddressKey? {
        val segments = normalizedKey.value.split("|")
        return when {
            segments.size == 4 && segments.all { it.isNotBlank() } -> {
                RelaxedAddressKey("${segments[0]}|${segments[2]}|${segments[3]}")
            }

            segments.size == 3 && segments.all { it.isNotBlank() } -> {
                RelaxedAddressKey(normalizedKey.value)
            }

            else -> null
        }
    }
}

private fun assertCondition(condition: Boolean, message: String): Unit {
    check(condition) { message }
}

private fun <ValueType> assertEquals(expected: ValueType, actual: ValueType, message: String): Unit {
    check(expected == actual) { "$message: expected=$expected actual=$actual" }
}

private fun resolverOf(vararg entries: OfflineGeoEntry): OfflineGeoResolver {
    return OfflineGeoResolver.fromEntries(
        entries = entries.asList(),
        addressKeyPolicy = TestAddressKeyPolicy,
        coordinateValidator = FiniteCoordinateValidator,
    )
}

private fun entry(rawKey: String, latitude: Double, longitude: Double): OfflineGeoEntry {
    return OfflineGeoEntry(
        rawKey = RawAddressKey(rawKey),
        coordinate = GeoCoordinate(latitude = latitude, longitude = longitude),
    )
}

private fun normalizedKeyUsesExactFixture(): Unit {
    val expectedCoordinate = GeoCoordinate(latitude = 10.5, longitude = 20.5)
    val resolver = resolverOf(entry("zone alpha / route one / unit 7", 10.5, 20.5))

    val result = resolver.resolve(RawAddressKey("  ZONE   ALPHA / ROUTE ONE / UNIT 7  "))

    assertEquals(
        GeoResolutionResult.Resolved(
            coordinate = expectedCoordinate,
            matchKind = GeoMatchKind.EXACT,
        ),
        result,
        "normalized exact key must resolve the fixture",
    )
}

private fun uniqueRelaxedKeyResolvesWithoutGuessing(): Unit {
    val expectedCoordinate = GeoCoordinate(latitude = 11.0, longitude = 21.0)
    val resolver = resolverOf(entry("region-a|subregion-a|route-1|unit-1", 11.0, 21.0))

    val result = resolver.resolve(RawAddressKey("region-a|route-1|unit-1"))

    assertEquals(
        GeoResolutionResult.Resolved(
            coordinate = expectedCoordinate,
            matchKind = GeoMatchKind.RELAXED_UNIQUE,
        ),
        result,
        "a unique relaxed key must resolve",
    )
}

private fun ambiguousRelaxedKeyNeverChoosesCandidate(): Unit {
    val resolver = resolverOf(
        entry("region-a|subregion-a|route-1|unit-1", 11.0, 21.0),
        entry("region-a|subregion-b|route-1|unit-1", 12.0, 22.0),
    )

    val result = resolver.resolve(RawAddressKey("region-a|route-1|unit-1"))

    assertEquals(
        GeoResolutionResult.AmbiguousRelaxedKey,
        result,
        "an ambiguous relaxed key must not select a coordinate",
    )
}

private fun malformedKeyAndInvalidCoordinateAreRejected(): Unit {
    val resolver = resolverOf(
        entry("region-a|subregion-a|route-1|unit-1", Double.NaN, 21.0),
    )

    assertEquals(
        GeoResolutionResult.InvalidAddressKey,
        resolver.resolve(RawAddressKey("   ")),
        "a blank address key must be rejected",
    )
    assertEquals(
        GeoResolutionResult.UnknownAddressKey,
        resolver.resolve(RawAddressKey("region-a|route-1|unit-1")),
        "an invalid coordinate must not enter the offline index",
    )
}

private fun firstExactCoordinateIsStable(): Unit {
    val firstCoordinate = GeoCoordinate(latitude = 11.0, longitude = 21.0)
    val resolver = resolverOf(
        entry("region-a|subregion-a|route-1|unit-1", 11.0, 21.0),
        entry("region-a|subregion-a|route-1|unit-1", 12.0, 22.0),
    )

    val result = resolver.resolve(RawAddressKey("region-a|subregion-a|route-1|unit-1"))

    assertCondition(
        result == GeoResolutionResult.Resolved(firstCoordinate, GeoMatchKind.EXACT),
        "the first exact coordinate must remain stable",
    )
}

object OfflineGeoResolverTest {
    @JvmStatic
    fun main(args: Array<String>): Unit {
        normalizedKeyUsesExactFixture()
        uniqueRelaxedKeyResolvesWithoutGuessing()
        ambiguousRelaxedKeyNeverChoosesCandidate()
        malformedKeyAndInvalidCoordinateAreRejected()
        firstExactCoordinateIsStable()
    }
}
