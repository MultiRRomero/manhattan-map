
def enum(**enums):
    return type('Enum', (), enums)

Fees = enum(
    NO_FEE = 'nfb',
    FEE = 'fee',
)

Neighborhoods = enum(
    BATTERY_PARK=120,
    CHELSEA=134,
    CHINATOWN_ITALY=160,
    DOWNTOWN=121,
    EAST_HARLEM=159,
    EAST_VILLAGE=129,
    FINANCIAL=122,
    FLATIRON=133,
    GRAMERCY=132,
    GREENWICH=127,
    HARLEM=141,
    INWOOD=140,
    LOWER_EAST_SIDE=126,
    MIDTOWN=135,
    MIDTOWN_EAST=136,
    MIDTOWN_WEST=137,
    MURRAY=131,
    NOLITA=125,
    SOHO=124,
    TRIBECA=123,
    UNION_SQUARE=130,
    UPPER_EAST_SIDE=139,
    UPPER_WEST_SIDE=138,
    WEST_VILLAGE=128,
)
