"""CHelper: a beginner-friendly chemistry calculator using Drafter.

This website uses molar masses from ChemPy.
ChemPy is not imported here because it wasn't working with the website
part of the project and was producing errors.
"""

from dataclasses import dataclass, field
from drafter import *


MOLAR_MASSES = {
    "H2": 2.016,
    "O2": 31.998,
    "H2O": 18.015,
    "CO2": 44.009,
    "CO": 28.010,
    "CH4": 16.043,
    "N2": 28.014,
    "NH3": 17.031,
    "NaCl": 58.443,
    "Na": 22.990,
    "Cl2": 70.906
}


@dataclass
class ReactionCalculation:
    """Holds the results of one stoichiometry calculation"""
    equation: str
    limiting_reactant: str
    product: str
    theoretical_yield: float
    actual_yield: float
    percent_yield: float
    remaining_reactants: str
    heat_description: str
    heat_per_mole: float
    total_heat: float
    show_enthalpy: bool


@dataclass
class State:
    """Remembers the  values and calculations"""
    equation: str = "2 H2 + O2 -> 2 H2O"
    reactant_masses: str = "H2 = 4.0\nO2 = 16.0"
    actual_mass: str = "10.0"
    delta_h: str = "-571.6"
    show_enthalpy: bool = True
    message: str = ""
    calculations: list[ReactionCalculation] = field(default_factory=list)
    calculation_count: int = 0


set_website_title("CHelper")
set_site_information(
    author="Christian Hoffman",
    description="A beginner-friendly stoichiometry calculator.",
    sources=[
        "OpenStax Chemistry 2e, Chapter 4",
        "ChemPy: used locally to prepare molar mass values",
        "NIH PubChem: chemistry reference"
    ],
    planning=["Planning_Design.docx", "site_mockup.png"],
    links=[
        "https://github.com/bjodah/chempy",
        "https://pubchem.ncbi.nlm.nih.gov/",
        "https://openstax.org/details/books/chemistry-2e"
    ]
)
hide_debug_information()
set_website_framed(False)


def get_molar_mass(formula: str) -> float:
    """Gets a chemical's molar mass from the ChemPy-prepared table"""
    if formula in MOLAR_MASSES:
        return MOLAR_MASSES[formula]
    else:
        raise ValueError("Unsupported chemical: " + formula)


def read_chemicals(text: str) -> dict:
    """Reads coefficients and formulas from one side of an equation"""
    chemicals = {}

    for item in text.split("+"):
        parts = item.strip().split()

        if len(parts) == 0:
            raise ValueError("Each side needs a chemical formula.")
        elif len(parts) == 1:
            coefficient = 1
            formula = parts[0]
        elif len(parts) == 2:
            coefficient = int(parts[0])
            formula = parts[1]
        else:
            raise ValueError("Use spaces, like 2 H2 + O2.")

        if coefficient <= 0:
            raise ValueError("Coefficients have to be positive.")
        if formula in chemicals:
            raise ValueError("Repeated chemical: " + formula)

        get_molar_mass(formula)
        chemicals[formula] = coefficient

    return chemicals


def get_reaction(equation: str) -> tuple:
    """Split an already-balanced equation into reactants and products"""
    sides = equation.split("->")

    if len(sides) != 2:
        raise ValueError("Use only one -> between reactants and products.")

    reactants = read_chemicals(sides[0])
    products = read_chemicals(sides[1])
    return reactants, products


def get_reactant_masses(mass_text: str, reactants: dict) -> dict:
    """Read reactant masses, one per line, such as H2 = 4.0."""
    masses = {}

    for line in mass_text.split("\n"):
        if line.strip() != "":
            parts = line.split("=")
            if len(parts) != 2:
                raise ValueError("Write each mass like H2 = 4.0.")

            formula = parts[0].strip()
            mass = float(parts[1].strip())

            if formula not in reactants:
                raise ValueError(formula + " is not a reactant.")
            if mass <= 0:
                raise ValueError("Reactant masses must be positive")
            if formula in masses:
                raise ValueError("Repeated mass for " + formula)

            masses[formula] = mass

    for formula in reactants:
        if formula not in masses:
            raise ValueError("Missing mass for " + formula)

    return masses


def calculate(equation: str, mass_text: str, actual_text: str,
              delta_h_text: str, show_enthalpy: bool) -> ReactionCalculation:
    """Calculate the limiting reactant, yields, leftovers, and heat."""
    reactants, products = get_reaction(equation)
    masses = get_reactant_masses(mass_text, reactants)
    actual_mass = float(actual_text)

    if actual_mass < 0:
        raise ValueError("Actual product mass cannot be negative.")

    # First, find how many complete reaction sets each reactant allows.
    limiting_reactant = ""
    smallest_amount = 0.0
    first_reactant = True

    for formula in reactants:
        coefficient = reactants[formula]
        moles = masses[formula] / get_molar_mass(formula)
        possible_reactions = moles / coefficient

        if first_reactant or possible_reactions < smallest_amount:
            smallest_amount = possible_reactions
            limiting_reactant = formula
            first_reactant = False

    # Use the first product on the right side of the equation.
    product = ""
    for formula in products:
        product = formula
        break

    product_coefficient = products[product]
    product_molar_mass = get_molar_mass(product)
    theoretical_moles = smallest_amount * product_coefficient
    theoretical_yield = theoretical_moles * product_molar_mass
    percent_yield = actual_mass / theoretical_yield * 100

    # Find the reactant masses left over after theoretical completion.
    remaining = ""
    for formula in reactants:
        starting_moles = masses[formula] / get_molar_mass(formula)
        used_moles = smallest_amount * reactants[formula]
        leftover_moles = starting_moles - used_moles

        if leftover_moles < 0:
            leftover_moles = 0

        leftover_mass = leftover_moles * get_molar_mass(formula)
        remaining += formula + ": " + str(round(leftover_mass, 3)) + " g; "

    heat_description = "Not calculated"
    heat_per_mole = 0.0
    total_heat = 0.0

    if show_enthalpy:
        # delta H is for the balanced equation AS WRITTEN.
        delta_h = float(delta_h_text)
        heat_per_mole = delta_h / product_coefficient
        actual_product_moles = actual_mass / product_molar_mass
        total_heat = heat_per_mole * actual_product_moles

        if delta_h < 0:
            heat_description = "Exothermic"
        elif delta_h > 0:
            heat_description = "Endothermic"
        else:
            heat_description = "No heat change"

    return ReactionCalculation(
        equation, limiting_reactant, product, theoretical_yield,
        actual_mass, percent_yield, remaining, heat_description,
        heat_per_mole, total_heat, show_enthalpy
    )


def navigation() -> list:
    """Builds buttons that appear on the website pages"""
    return [
        Button("Home", "index"),
        Button("Calculator", "reaction_input"),
        Button("Results", "view_results"),
        Button("History", "view_history"),
        Button("About", "about_page")
    ]


@route
def index(state: State) -> Page:
    """Displays the home page"""
    return Page(state, [
        Header("CHelper", 1),
        Paragraph("Enter a balanced equation, reactant masses, and the actual product mass"),
        Paragraph("Find limiting reactants, product yields, leftovers, and reaction heat"),
        Button("Start Calculating", "reaction_input"),
        Button("About CHelper", "about_page")
    ])


@route
def reaction_input(state: State) -> Page:
    """Display the form for entering a chemistry reaction."""
    contents = [
        Header("CHelper Calculator", 1),
        Paragraph("Balanced equation (example: 2 H2 + O2 -> 2 H2O)"),
        TextBox("equation", state.equation),
        Paragraph("Reactant masses in grams, one per line:"),
        TextArea("mass_text", state.reactant_masses, rows=4),
        Paragraph("Actual mass of the FIRST product collected (g):"),
        TextBox("actual_text", state.actual_mass),
        Paragraph("Reaction enthalpy, delta H (kJ for the equation as written):"),
        TextBox("delta_h_text", state.delta_h),
        CheckBox("show_enthalpy", state.show_enthalpy),
        " Calculate reaction heat\n",
        Button("Calculate", "calculate_stoich")
    ]

    if state.message != "":
        contents.append(Paragraph(state.message))


    return Page(state, contents)


@route
def calculate_stoich(state: State, equation: str, mass_text: str,
                     actual_text: str, delta_h_text: str,
                     show_enthalpy: bool) -> Page:
    """Saves inputs, calculates the result, and adds it to history"""
    state.equation = equation
    state.reactant_masses = mass_text
    state.actual_mass = actual_text
    state.delta_h = delta_h_text
    state.show_enthalpy = show_enthalpy

    try:
        result = calculate(
            equation, mass_text, actual_text, delta_h_text, show_enthalpy
        )
        state.calculations.append(result)
        state.calculation_count += 1
        state.message = ""
        return view_results(state)
    except (ValueError, TypeError, ZeroDivisionError) as error:
        state.message = "Error: " + str(error)
        return reaction_input(state)


@route
def view_results(state: State) -> Page:
    """Shows the most recently saved result"""
    contents = [Header("Calculation Results", 1)]

    if len(state.calculations) == 0:
        contents.append(Paragraph("No calculations completed yet."))
    else:
        result = state.calculations[-1]
        contents.append(Paragraph("Equation: " + result.equation))
        contents.append(Paragraph("Limiting reactant: " + result.limiting_reactant))
        contents.append(Paragraph("Product: " + result.product))
        contents.append(Paragraph(
            "Theoretical yield: " + str(round(result.theoretical_yield, 3)) + " g"
        ))
        contents.append(Paragraph(
            "Actual yield: " + str(round(result.actual_yield, 3)) + " g"
        ))
        contents.append(Paragraph(
            "Percent yield: " + str(round(result.percent_yield, 2)) + "%"
        ))
        contents.append(Paragraph("Remaining reactants: " + result.remaining_reactants))

        if result.percent_yield > 100:
            contents.append(Paragraph(
                "Yield above 100%"
            ))
        if result.show_enthalpy:
            contents.append(Paragraph("Reaction type: " + result.heat_description))
            contents.append(Paragraph(
                "Heat per mole of product: "
                + str(round(result.heat_per_mole, 3)) + " kJ/mol"
            ))
            contents.append(Paragraph(
                "Estimated heat for actual product amount: "
                + str(round(result.total_heat, 3)) + " kJ"
            ))

    contents.extend(navigation())
    return Page(state, contents)


@route
def view_history(state: State) -> Page:
    """Lists previous calculations and provides delete buttons"""
    contents = [
        Header("Calculation History", 1),
        Paragraph("Calculations performed: " + str(state.calculation_count))
    ]

    if len(state.calculations) == 0:
        contents.append(Paragraph("You have no saved calculations, loser"))

    for number in range(len(state.calculations)):
        result = state.calculations[number]
        contents.append(Header("Calculation " + str(number + 1), 2))
        contents.append(Paragraph("Equation: " + result.equation))
        contents.append(Paragraph("Limiting reactant: " + result.limiting_reactant))
        contents.append(Paragraph(
            "Theoretical yield: " + str(round(result.theoretical_yield, 3)) + " g"
        ))
        contents.append(Paragraph(
            "Percent yield: " + str(round(result.percent_yield, 2)) + "%"
        ))
        contents.append(Button(
            "Delete Calculation " + str(number + 1),
            "delete_calculation", [Argument("number", number)]
        ))

    contents.extend(navigation())
    return Page(state, contents)


@route
def delete_calculation(state: State, number: int) -> Page:
    """Remove one calculation from history."""
    if 0 <= number < len(state.calculations):
        state.calculations.pop(number)
        state.message = "Calculation deleted."
    return view_history(state)


@route
def about_page(state: State) -> Page:
    """Explains the website and gives sources and information"""
    contents = [
        Header("About CHelper", 1),
        Paragraph("CHelper is a classroom stoichiometry calculator."),
        Paragraph(
            "The user must supply an already-balanced reaction with spaces "
            "between coefficients and formulas (for example: 2 H2)."
        ),
        Paragraph(
            "Molar masses were prepared using ChemPy in Thonny and website "
            "currently uses a small dictionary because ChemPy isn't working in drafter"
        ),
        Paragraph(
            "It calculates theoretical yield and remaining reactants assuming "
            "the limiting reactant is completely used up"
        ),
        Paragraph(
            "The heat estimate uses entered delta H"
        ),
        Paragraph(
            "Only formulas in the dictionary are supported"
        ),
        Header("References", 2),
        Paragraph("OpenStax Chemistry 2e, Chapter 4"),
        Paragraph("ChemPy, https://github.com/bjodah/chempy"),
        Paragraph("NIH PubChem, https://pubchem.ncbi.nlm.nih.gov/")
    ]
    contents.extend(navigation())
    return Page(state, contents)


start_server(State())

