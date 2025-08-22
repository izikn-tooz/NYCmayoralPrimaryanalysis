import streamlit as st
from pathlib import Path
from streamlit.components.v1 import html as st_html
import pandas as pd
import requests
from typing import Optional

# =============================
# Config
# =============================

st.set_page_config(
    page_title="How did diversity affect the recent New York City Democratic Mayoral Primary? Some lessons from the data.",
    layout="wide"
)
st.caption("An Independent Analysis by Isaac Tasch")

ASSETS_DIR = Path(".")

# -----------------------------
# Remote files (GitHub Releases)
# -----------------------------
USER   = "izikn-tooz"
REPO   = "NYCmayoralPrimaryanalysis"
TAG    = "v1Maps"  # <- your published release tag

DOWNLOAD_BASE = f"https://github.com/{USER}/{REPO}/releases/download/{TAG}/"

def download_file(remote_name: str, local_path: Path):
    """Download release asset if missing locally."""
    if local_path.exists():
        return local_path
    try:
        url = DOWNLOAD_BASE + remote_name
        st.info(f"Fetching {remote_name} from GitHub Releases…")
        resp = requests.get(url)
        resp.raise_for_status()
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(resp.content)
        st.success(f"Downloaded {remote_name}")
    except Exception as e:
        st.error(f"Failed to fetch {remote_name} from {url}: {e}")
    return local_path

# -----------------------------
# Paths
# -----------------------------

# HTML maps (large files via GitHub Releases)
FULL_CENTER_PATH   = download_file(
    "overlay_results_top_with_slider_dots_bottom_static.html",
    ASSETS_DIR / "Primary Maps/overlay_results_top_with_slider_dots_bottom_static.html"
)
BOTTOM_LEFT_MAP_PATH  = download_file(
    "personal_diversity_heatmap_no_water_overlap.html",
    ASSETS_DIR / "Primary Maps/personal_diversity_heatmap_no_water_overlap.html"
)
BOTTOM_RIGHT_MAP_PATH = download_file(
    "shannon_index_heatmap_no_water_overlap.html",
    ASSETS_DIR / "Primary Maps/shannon_index_heatmap_no_water_overlap.html"
)

# Images (safe to keep in repo)
PERSONAL_DIVERSITY_IMG = ASSETS_DIR / "Person_diversity_example.png"
PERSONAL_VS_ZOHRAN_IMG = ASSETS_DIR / "Personal_Diversity_vs_Proportion_Zohran.png"
SHANNON_VS_ZOHRAN_IMG  = ASSETS_DIR / "ShannonindexvProportionZohran.png"
QUEENS_EXAMPLE_IMG     = ASSETS_DIR / "Queens Example.png"

# Excel files
LOGIT_FULL_XLSX       = ASSETS_DIR / "LogitFull.xlsx"
LOGIT_PARTIAL_XLSX    = ASSETS_DIR / "LogitPartial.xlsx"
LOGIT_BIVAR_XLSX      = ASSETS_DIR / "LogitBivariate.xlsx"
MULTI_UNWEIGHTED_XLSX = ASSETS_DIR / "Multinomial Unweighted.xlsx"
MULTI_WEIGHT_XLSX     = ASSETS_DIR / "Multinomial Weighted.xlsx"

# Heights
DEFAULT_FULL_HEIGHT = 600
DEFAULT_PAIR_HEIGHT = 600

# =============================
# CSS tweaks
# =============================
st.markdown(
    """
    <style>
      [data-testid="stAppViewContainer"] .main .block-container {
        max-width: 100% !important;
        padding-left: 6px; padding-right: 6px;
      }
      div[data-testid="stIFrame"] { width: 100% !important; }
      div[data-testid="stIFrame"] > iframe { width: 100% !important; }
      iframe { max-width: 100% !important; }
      body { overflow-x: hidden; }
      .note-box {
        border: 1px solid rgba(0,0,0,0.12);
        background: rgba(0,0,0,0.03);
        border-radius: 10px;
        padding: 14px 16px;
        margin-top: 8px;
        font-size: 0.95rem;
        line-height: 1.35rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================
# Helpers (HTML minification + immediate render)
# =============================

# Optional minifier: if not available, we skip minification gracefully
try:
    import htmlmin
    HAVE_HTMLMIN = True
except Exception:
    HAVE_HTMLMIN = False

@st.cache_data(show_spinner=False)
def load_html_text(p: Path, do_minify: bool = True) -> str:
    """Read HTML text; optionally minify large Folium exports to trim payload."""
    txt = p.read_text(encoding="utf-8")
    if do_minify and HAVE_HTMLMIN and len(txt) > 200_000:
        txt = htmlmin.minify(
            txt,
            remove_comments=True,
            reduce_empty_attributes=True,
            remove_optional_attribute_quotes=False,
            remove_empty_space=True,
        )
    return txt

def render_html_now(path: Path, height: int, width_px: Optional[int] = None, minify: bool = True):
    """Inject (possibly minified) HTML into an iframe immediately."""
    if not path.exists():
        st.error(f"File not found: {path}")
        return
    st_html(load_html_text(path, do_minify=minify), height=height, width=width_px, scrolling=False)

# =============================
# Sidebar controls
# =============================
st.sidebar.header("Display Settings")
full_h = st.sidebar.slider("Full-width map height (px)", 400, 1600, DEFAULT_FULL_HEIGHT, 10)
pair_h = st.sidebar.slider("Bottom pair height (px)", 300, 1400, DEFAULT_PAIR_HEIGHT, 10)
if st.sidebar.button("🔄 Refresh maps"):
    load_html_text.clear()

# =============================
# Page
# =============================
st.markdown(
    "<h1 style='text-align: center;'>How did diversity affect the recent New York City Democratic Mayoral Primary? Some lessons from the data.</h1>",
    unsafe_allow_html=True
)
# Introductory text below title
st.markdown(
    """
    <div class="note-box">
    The 2025 New York City mayoral election is fast approaching with November 4th just over 10 weeks away.  
    The Democratic Primary in June that saw the former New York State Governor, and democratic establishment preference, Andrew Cuomo, faceoff against the self-described Democratic Socialist Zohran Mamdani.  

    Mamdani won the primary with 44% of the vote, compared to Cuomo’s 36%, which ignited a media frenzy to explain the victory of a politically recalcitrant socialist over a party veteran with establishment backing.  

    Much of the mainstream media blamed it on Mamdani’s social media performance and appeal to young voters. Less liberal stations, probably correctly, assumed that it was due to his policy positions.  

    Without a clear answer for correlations among social characteristics and the socialist vote, one common theme among journalists from the right to the left was to question why the “black vote” skewed so heavily toward Cuomo, despite his representative whiteness and overall affluent affect. Some sources were correct to point out that the “black vote” is not a monolith and color-based racial identity is far from deterministic of one’s politics.  

    With this reality in mind, this statistical brief is here to suggest that one of the most influential factors in Mamdani’s victory over Cuomo was diversity. Primarily racial diversity, though ethnic and cultural diversity as well. The theory to be tested is that geographic racial (as well as ethnic/cultural) homogeneity creates a political ‘enclave’ effect that influences voters to become less friendly to socialist politics, regardless of whether that homogeneity is white, black, Hispanic, Asian or otherwise.  

    Below is a map of New York public housing tracts and electoral districts, along with how those districts voted in the recent democratic mayoral primary, overlayed with a dot-density graph of racial distribution at the block-level provided by the 2020 Decennial Census conducted by the U.S. Census Bureau. Dots were placed randomly within each block-level boundary. Each dot represents 40 respondents to the 2020 racial survey. With each block-level geographic subset containing a count of each racial category, each dot was placed by a simulation within that block subset accounting for set of 40 respondents with the same racial and block category.
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# FULL-WIDTH (overlay map) — LOAD IMMEDIATELY
# -----------------------------
st.subheader("Overlay Results")
render_html_now(FULL_CENTER_PATH, height=full_h, width_px=2200, minify=True)

# Text beneath overlay map
st.markdown(
    """
    <div class="note-box">
    To measure the relative diversity of different election districts, the dot density map was overlayed with a map of New York City election districts and census tracts.  
    Since each dot placed by the simulation had a discrete location, each dot had a unique electoral district and census tract match.  
    The racial category counts of each election district were then summed by counting the number of dots within each geographic subcategory as placed by the simulation. Below are two different measures of diversity according to the simulated data.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# -----------------------------
# BOTTOM ROW: two maps, side-by-side — LOAD BOTH IMMEDIATELY
# -----------------------------
st.subheader("Diversity Heatmaps")
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("##### Personal Diversity Heatmap")
    render_html_now(BOTTOM_LEFT_MAP_PATH, height=pair_h, width_px=1200, minify=True)

    # Image below map
    if PERSONAL_DIVERSITY_IMG.exists():
        st.image(str(PERSONAL_DIVERSITY_IMG), use_container_width=True)
    else:
        st.error(f"Image not found: {PERSONAL_DIVERSITY_IMG}")

    # Text box below image
    st.markdown(
        """
        <div class="note-box">
        To determine the Personal Diversity Index, dots were taken from the Overlay Results map, which placed dots according to the simulation. For the calculation of the personal diversity score, every dot rendered represented one person (rather than 40) and each dot was placed randomly with street level restrictions to simulate the distribution of people in New York City according to their actual geographic distribution of residence. Each dot was then given a personal diversity score that was equal to the number of dots that belonged to a different racial category than the reference dot, divided by the total number of dots within 70 meters of the reference dot. (70 meters as a radius was chosen as that distance is about half the length of an average city block, and roughly the width of most highways that pass through the city). In the example above, the circle pictured has a roughly 70-meter radius with the reference dot at the center. Within 70 meters of the reference dot there are 15 total dots, where 10 of those dots are of a different racial category. Since there are 15 dots total, with 10 dots of a different racial category, the Personal Diversity Index for the reference dot = 10/15 = 0.75. In the image above, each dot is equal to roughly 40 people. To determine the Personal Diversity Index of each distinct election district in New York City, every dot representing one respondent to the racial survey included in the 2020 Decennial Census of Population and Housing, was placed by the simulation and then assigned a Personal Diversity Index determined by their 70-meter radius environment. For each election district, these Personal Diversity Indices were then summed and divided by the total number of respondents placed by the simulation within each election district.
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown("##### Shannon Index Heatmap")
    render_html_now(BOTTOM_RIGHT_MAP_PATH, height=pair_h, width_px=1200, minify=True)

    # --- Shannon Index explanation (styled note-box + proper LaTeX rendering) ---

    # Lead-in + formula header (styled)
    st.markdown(
        """
        <div class="note-box">
        To determine the Shannon Diversity Index, proportions of each racial category were found by counting
        the number of dots that were placed in each election district by the simulation of block-level racial data.
        The relative proportions of each racial category within each election district were then determined and
        applied to the Shannon-Diversity Index formula, a standard measure of categorical diversity within a geographic subset:
        </div>
        """,
        unsafe_allow_html=True,
    )

    # The formula (LaTeX)
    st.latex(r"H' = -\sum_{i=1}^{S} p_i \ln(p_i)")

    st.markdown(
        """
        <div class="note-box">
        Where p<sub>i</sub> is equal to the proportion of each racial category present in a given election district.  
        Note that there is no control for evenness such that election districts with a higher number of distinct
        racial categories will have a higher Shannon-Diversity Index than those with fewer racial categories
        even if they share an equal distribution of proportions.  

        For example, if one election district contains only two racial categories, where they are distributed equally
        p<sub>1</sub> = p<sub>2</sub> = 0.5, this election district will be considered less diverse than another election
        district with four racial categories where p<sub>1</sub> = p<sub>2</sub> = p<sub>3</sub> = p<sub>4</sub> = 0.25.
        </div>
        """,
        unsafe_allow_html=True,
    )
# -----------------------------
# NEW ROW: two images aligned level
# -----------------------------
img_col1, img_col2 = st.columns(2, gap="large")

with img_col1:
    if PERSONAL_VS_ZOHRAN_IMG.exists():
        st.image(str(PERSONAL_VS_ZOHRAN_IMG), use_container_width=True)
    else:
        st.error(f"Image not found: {PERSONAL_VS_ZOHRAN_IMG}")

with img_col2:
    if SHANNON_VS_ZOHRAN_IMG.exists():
        st.image(str(SHANNON_VS_ZOHRAN_IMG), use_container_width=True)
    else:
        st.error(f"Image not found: {SHANNON_VS_ZOHRAN_IMG}")

# -----------------------------
# Centered header below both columns
# -----------------------------
st.markdown(
    "<h2 style='text-align:center; margin-top:30px;'>"
    "Five Models to Estimate the Effect of Diversity on Zohran Mamdani’s Primary Results by Election District"
    "</h2>",
    unsafe_allow_html=True,
)

# -----------------------------
# Explanatory text below header
# -----------------------------
st.markdown(
    """
    <div class="note-box">
    One of the principal challenges in estimating such effects is the issue of aggregation and the ecological fallacy that arises from the chosen aggregation method for geographically correlated parameters.  

    In order to derive the most accurate measurements at the election district level, each individual from the initial racial distribution simulation was assigned a census tract FIPS code according to where their dot was placed and the unique census tract they were contained in. Then all of the parameters belonging to the individuals with the same NYC election district code were summed and divided by the number of individuals within that district to find the average values of each parameter within each election district.  

    A description of each parameter is below:  
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Variable definitions (updated) — note-box
# -----------------------------
st.markdown(
    """
    <div class="note-box">
      <b>Personal Diversity Score</b> – As described above, these data were provided by the 2020 Decennial Census conducted by the U.S. Census Bureau.
      The block-level counts may be found here:
      <a href="https://www.nhgis.org/" target="_blank">NHGIS</a>.
      <br><br>

      <b>In Public Housing</b> – Similar to Personal Diversity Score, the proportion of each election district living in public housing was estimated by totaling the number of dots, placed individually using the simulation which utilized the block-level data provided by the 2020 Decennial Census.
      A map of New York City’s public housing districts was then overlayed and the number of dots within each overlay subset were counted.
      The GIS data on public housing is provided by the New York City Housing Authority and can be found here:
      <a href="https://www.nyc.gov/site/nycha/about/developments.page" target="_blank">NYCHA Developments</a>.
      <br><br>

      <b>Turnout</b> – Vote information was collected from the New York City Board of Elections.
      The variable turnout is equal to the number of people that voted in each election district divided by the total number of registered Democrats within that election district.
      These data may be found here:
      <a href="https://vote.nyc/page/election-results-summary" target="_blank">NYC BOE Results</a>.
      <br><br>

      <b>2024 Arrests Per Cap</b> – This is a census-level variable.
      In each census district the total number of arrests were summed and then divided by the number of people recorded by the census to live in that district.
      Since every dot placed by the simulation of population by race provided by the 2020 U.S. Decennial Census had a unique census tract FIPS code, this average was attributed to every “dot” (person) that fell within a particular census tract.
      Each of those individuals additionally had a unique election district code.
      For each election district, all characteristics of every dot were then summed and divided by the number of dots within that election district; those averages, such as 2024 arrests per cap, were then assigned to that election district.
      The data on 2024 arrests per capita can be found here:
      <a href="https://www.nyc.gov/site/nypd/stats/crime-statistics/citywide-crime-stats.page" target="_blank">NYPD Crime Stats</a>.
      <br><br>

      <b>Average Median Income</b> – This is a census-level variable.
      Median income per census tract was assigned to each dot placed by the simulation with the matching unique census tract FIPS code.
      These median incomes per dot were then summed and divided according to the group of dots with the same election district code.
      The average was then assigned to that election district.
      <i>The data on median income may be found here:</i> 
      <a href="https://data.census.gov/table/" target="_blank">data.census.gov (ACS)</a>.
      <br><br>

      <b>% Non Native</b> – This is a census-level variable. Provided by the 2023 American Community Survey, this variable is defined by the U.S. Census Bureau as the total number of individuals “U.S. citizen by naturalization” + “Not a U.S. citizen” within each census tract.
      These data were attributed to each election district in the same manner as 2024 arrests per cap and average median income.
      These data may be found here:
      <a href="https://data.census.gov/table/" target="_blank">data.census.gov (ACS)</a>.
      <br><br>

      <b>% Multi Lingual</b> – This is a census-level variable. Provided by the 2023 American Community Survey, this variable is defined by the U.S. Census Bureau as “the total number of people 5 years and over that speak a language other than English”.
      These data were attributed to each election district in the same manner as 2024 arrests per cap, average median income, and % non native.
      These data may be found here:
      <a href="https://data.census.gov/table/" target="_blank">data.census.gov (ACS)</a>.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="note-box">

    Since the personal diversity score and the Shannon diversity index track with a correlation coefficient of 0.96, the models below utilize the personal diversity score as the primary independent variable for diversity since its proportionality between 0 and 1 makes its effects on vote proportions easier to interpret and because it stands to reason that the personal diversity score may be a better measure of ‘felt’ diversity than the Shannon diversity index. This is because the Shannon diversity index is calculated with probability at the election district level, whereas the personal diversity score is calculated for each person at the individual level.  

    To estimate the effects of diversity on the election outcome in the New York Democratic Mayoral Primary, several 'full' models that regress the variables average personal diversity score within the election district, average census tract level percent of individuals that are multi lingual, average census tract level percent of individuals that are non-native, census tract level average median income, average census tract level number of arrests per capita, the proportion of individuals in the election district that live in public housing and finally the turnout per election district on the proportion of the democratic primary vote in each election district that was awarded to Zohran Mamdani are estimated.  

    The partial version then models the proportion of the vote that went to Zohran Mamdani per election district as a function of only the average personal diversity score of the election district, the proportion of individuals in the election district living in public housing and the turnout per election district. These are the distinctly election-district level variables. 

    The final bivariate model regresses only the average personal diversity score per election district on the proportion of the vote that went to Zohran Mamdani within that election district.  

    Below are two distinct models. First, a standard logit model with three parameter specifications, full, partial and bivariate that each utilize the proportion of the vote that went to Zohran Mamdani per election distrcit as the dependant variable. Then second, a multinomial logit model with a full specification that uses each each election district's liklihood of choosing each Democratic Mayoral Primary candidate over Cuomo (as the baseline) as the dependant variable. The first specification of the multinomial logit model gives each election district equal weight regardless of the number of voters. The second specification incorporates weights for the number of people that voted in each election district in the estimation of the parameter's coefficients.   

    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# TABLE: show Excel like the provided file
# -----------------------------
st.markdown(
    "### Regression Results (Logit – Full Specification), Number of Observations: 3971, Psuedo R-Squared: 0.045")
if LOGIT_FULL_XLSX.exists():
    try:
        df_logit = pd.read_excel(LOGIT_FULL_XLSX, engine="openpyxl", sheet_name="Sheet1")
        st.dataframe(df_logit, use_container_width=True)
        st.download_button(
            "Download table as CSV",
            data=df_logit.to_csv(index=False).encode("utf-8"),
            file_name="LogitFull_table.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"Failed to load Excel file: {LOGIT_FULL_XLSX}\n\n{e}")
else:
    st.error(f"File not found: {LOGIT_FULL_XLSX}")

# -----------------------------
# TABLE: LogitPartial.xlsx ("sheet 1")
# -----------------------------
st.markdown(
    "### Regression Results (Logit – Partial Specification), Number of Observations: 3971, Psuedo R-Squared: 0.03688")
if LOGIT_PARTIAL_XLSX.exists():
    try:
        df_logit_partial = pd.read_excel(LOGIT_PARTIAL_XLSX, engine="openpyxl", sheet_name="Sheet1")
        st.dataframe(df_logit_partial, use_container_width=True)
        st.download_button(
            "Download partial table as CSV",
            data=df_logit_partial.to_csv(index=False).encode("utf-8"),
            file_name="LogitPartial_table.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"Failed to load Excel file: {LOGIT_PARTIAL_XLSX}\n\n{e}")
else:
    st.error(f"File not found: {LOGIT_PARTIAL_XLSX}")

# -----------------------------
# TABLE: LogitBivariate.xlsx ("sheet 1")
# -----------------------------
st.markdown(
    "### Regression Results (Logit – Bivariate Specification), Number of Observations: 3971, Psuedo R-Squared: 0.03036")
if LOGIT_BIVAR_XLSX.exists():
    try:
        try:
            df_logit_bivar = pd.read_excel(LOGIT_BIVAR_XLSX, engine="openpyxl", sheet_name="Sheet1")
        except Exception:
            try:
                df_logit_bivar = pd.read_excel(LOGIT_BIVAR_XLSX, engine="openpyxl", sheet_name="sheet 1")
            except Exception:
                df_logit_bivar = pd.read_excel(LOGIT_BIVAR_XLSX, engine="openpyxl")  # first sheet
        st.dataframe(df_logit_bivar, use_container_width=True)
        st.download_button(
            "Download bivariate table as CSV",
            data=df_logit_bivar.to_csv(index=False).encode("utf-8"),
            file_name="LogitBivariate_table.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"Failed to load Excel file: {LOGIT_BIVAR_XLSX}\n\n{e}")
else:
    st.error(f"File not found: {LOGIT_BIVAR_XLSX}")

st.markdown(
    """
    This first set of logit models estimate the regression as follows:  
    The coefficient $\\beta_j$ represents the change in log-odds of supporting Zohran for a 1-unit increase in $x_j$, holding all else constant.  

    Where,
    """,
    unsafe_allow_html=True,
)
st.latex(r"\beta_j = \frac{\partial}{\partial x_j} \log\!\left(\frac{\mu}{1 - \mu}\right)")
st.latex(r"\mu_i = \Pr(Y_i = 1 \mid X_i) = \frac{e^{X_i \beta}}{1 + e^{X_i \beta}}")

# =============================
# Interpretation: Logit marginal effects
# =============================
st.markdown(
    """
    Since the logit model estimates diminishing effects of the parameters at the extremes, here we find, where diversity is moderate, around a personal diversity score of **0.5**, an increase in diversity of about **1%** in the average personal diversity score of an election district is associated with an increase in in percentage points of the proportion of the vote that goes to Zohran Mamdani of approximately:
    """
)
st.latex(r"\frac{\partial \mu}{\partial \text{PDS}} = \beta \cdot \mu \cdot (1 - \mu) = 2.5687 \cdot 0.5 \cdot 0.5 = 0.642 \;\;")
st.markdown(
    """
    Thus the elasticity of the effect of diversity (for election districts with moderate diversity) on the proportion of the vote that went to Mamdani during the June democratic Mayoral Primary in NYC is equal to **0.00642/0.5 = 0.0138**, or 1.3%. This means that for a 1% increase in the average personal diversity score of a given election district, we would expect a 1.3% increase in the proportion of votes that went to Mamdani in that election district. This indicates a high sensitivity of New York Democratic Primary voter's likelihood of voting for Zohran Mamdani to their local racial diversity. 
    """
)

# -----------------------------
# TABLE: Multinomial Unweighted.xlsx (Sheet1)
# -----------------------------
st.markdown(
    "### Regression Results (Multinomial Logit — Unweighted), Number of Observations: 3971, Psuedo R-Squared: 0.26, Within-sample accuracy: 0.744")
if MULTI_UNWEIGHTED_XLSX.exists():
    try:
        try:
            df_multi_unw = pd.read_excel(MULTI_UNWEIGHTED_XLSX, engine="openpyxl", sheet_name="Sheet1")
        except Exception:
            try:
                df_multi_unw = pd.read_excel(MULTI_UNWEIGHTED_XLSX, engine="openpyxl", sheet_name="sheet 1")
            except Exception:
                df_multi_unw = pd.read_excel(MULTI_UNWEIGHTED_XLSX, engine="openpyxl")  # first sheet
        st.dataframe(df_multi_unw, use_container_width=True)
        st.download_button(
            "Download multinomial table as CSV",
            data=df_multi_unw.to_csv(index=False).encode("utf-8"),
            file_name="Multinomial_Unweighted_table.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"Failed to load Excel file: {MULTI_UNWEIGHTED_XLSX}\n\n{e}")
else:
    st.error(f"File not found: {MULTI_UNWEIGHTED_XLSX}")

# -----------------------------
# EXPLANATORY TEXT: Multinomial Logit Interpretation
# -----------------------------
st.markdown("---")
st.markdown("### Interpretation of Multinomial Logit Results")

st.markdown(
    """
    The multinomial logit model is motivated by the assumption that there is a latent utility function determining 
    individual candidate choice, i.e.
    """,
    unsafe_allow_html=True,
)
st.latex(r"U_{ij} = x_i^\top \beta_j + \varepsilon_{ij}")
st.markdown(
    """
    where individuals choose candidates while ranking them against one another.  

    Here we model choice *over* Cuomo (where choices for first rank in the rank-choice voting system are considered 
    mutually exclusive). With Cuomo as our baseline candidate, there are eleven other choices among the roster of 
    candidates in the New York City Democratic Mayoral Primary. Thus our model estimates
    """,
    unsafe_allow_html=True,
)
st.latex(r"P(Y_i = j \mid x_i) = p_{ij} = \frac{\exp(x_i^\top \beta_j)}{\sum_{m=1}^J \exp(x_i^\top \beta_m)}")
st.markdown("We normalize $\\beta_J = 0$, and thus estimate")
st.latex(r"p_{ij} = \frac{\exp(x_i^\top \beta_j)}{1 + \sum_{m=1}^{J-1} \exp(x_i^\top \beta_m)}, \quad j = 1, \dots, J-1.")
st.markdown("Finally, we have, in log-odds form,")
st.latex(r"\ln \!\left( \frac{P(Y_i = j)}{P(Y_i = J)} \right) = x_i^\top \beta_j.")

st.markdown(
    """
    Since the coefficient on the parameter *personal diversity score* is equal to $\\beta = 7.7009$, 
    measuring the effect of average personal diversity score per election district on the log-likelihood 
    that Mamdani wins over Cuomo in that election district (since all other candidates received negligible 
    proportions of the overall vote), we find that for every 1\\% increase in the average personal diversity 
    score of any given NYC election district, there is an increased chance of
    """,
    unsafe_allow_html=True,
)
st.latex(r"e^{7.7 \times 0.01} \approx 1.08")
st.markdown("i.e. an 8% increase in the odds of Zohran Mamdani winning over Andrew Cuomo.")
st.markdown(
    """
    The probability change is non-linear with reference to the original probability of Zohran Mamdani winning. 
    For example:
    """,
    unsafe_allow_html=True,
)
st.markdown(
    "- If there is a 20% chance Zohran Mamdani wins an election district, and that district’s average personal diversity score increases by 1%, then")
st.latex(r"\Delta p \approx 0.20 \cdot 0.80 \cdot 7.7 \cdot 0.01 = 0.0123 \quad (\approx +1.2 \text{ percentage points}).")
st.markdown("- If there is a 50% chance Zohran Mamdani wins an election district, then")
st.latex(r"\Delta p \approx 0.50 \cdot 0.50 \cdot 7.7 \cdot 0.01 = 0.019 \quad (\approx +1.9 \text{ points}).")
st.markdown("- If there is an 80% chance Zohran Mamdani wins an election district, then")
st.latex(r"\Delta p \approx 0.80 \cdot 0.20 \cdot 7.7 \cdot 0.01 = 0.0123 \quad (\approx +1.2 \text{ points}).")

st.markdown(
    """
    So, on average, there is a **1.3 percentage point increase** (since the effect is larger in the mid range of probability than in the tails) in the probability that Zohran Mamdani wins an 
    election district for every 1\\% increase in that district’s average personal diversity score.
    """,
    unsafe_allow_html=True,
)
st.write(
    "The elasticity of the effect of average personal diversity score on the likelihood "
    "that Zohran Mamdani won in any given election district, at the midpoint probability "
    "(a 50/50 chance), is estimated to be:"
)
st.latex(r"(1 - 0.5)\cdot 7.7009 \cdot 0.5 \approx 1.93\%, 51.93/50 = 1.0386%")
st.write("A nearly four percent elastic differential at the midpoint is quite large.")

# -----------------------------
# MULTINOMIAL WEIGHTED TABLE
# -----------------------------
st.markdown(
    "### Regression Results (Multinomial Logit — Unweighted), Number of Observations: 348281, Psuedo R-Squared: 0.2919, Within-sample accuracy: 0.770")
if MULTI_WEIGHT_XLSX.exists():
    try:
        try:
            df_multi_weight = pd.read_excel(MULTI_WEIGHT_XLSX, engine="openpyxl", sheet_name="Sheet1")
        except Exception:
            try:
                df_multi_weight = pd.read_excel(MULTI_WEIGHT_XLSX, engine="openpyxl", sheet_name="sheet 1")
            except Exception:
                df_multi_weight = pd.read_excel(MULTI_WEIGHT_XLSX, engine="openpyxl")  # fallback to first sheet
        st.dataframe(df_multi_weight, use_container_width=True)
        st.download_button(
            "Download multinomial weighted table as CSV",
            data=df_multi_weight.to_csv(index=False).encode("utf-8"),
            file_name="MultinomialWeighted_table.csv",
            mime="text/csv",
        )
    except Exception as e:
        st.error(f"Failed to load Excel file: {MULTI_WEIGHT_XLSX}\n\n{e}")
else:
    st.error(f"File not found: {MULTI_WEIGHT_XLSX}")

# -----------------------------
# Explanation text for weighted multinomial
# -----------------------------
st.markdown(
    r"""
    <div class="note-box">
    For the weighted multinomial logit model, election districts were weighted according to the size of their population that voted in the NYC Democratic Mayoral Primary.  
    Observations were duplicated according to the size of their voting population, with an average duplication of 87.7 per election district, which is why the number of observations is 348,281 instead of 3,971.  

    What is notable about this weighted model is that both the pseudo R-squared and in-sample predictive accuracy increased following the weighting procedure.  

    Where the weighted in-sample predictive accuracy is defined as:
    </div>
    """,
    unsafe_allow_html=True,
)
st.latex(
    r"""
    \text{Weighted Accuracy} 
    = \frac{\sum_{\text{ED}} \text{Total}_{ED} \cdot 1\{\text{predicted winner} = \text{actual winner}\}}
           {\sum_{\text{ED}} \text{Total}_{ED}}
    """
)

st.markdown(
    """
    <div class="note-box">
    This means that as the vote size of an election district increases, the model becomes significantly better at predicting the outcome. Along with the increased significance of the parameter coefficients over the unweighted model, this is strong evidence that the average personal diversity score, turnout, percent multi-lingual, and percent non-native are important determinants of a given election district’s likelihood to elect Zohran Mamdani.  

    Insofar as votes for Zohran Mamdani represent votes for socialist political sentiment, this should be considered strong evidence that the racial, ethnic, and cultural diversity of one’s community affects their likelihood of having sympathy for socialist politics.  

    Taken inversely, the findings provide reason to believe that racial, ethnic, and cultural homogeneity within a geographic community affect that communities liklihood to be adverse to socialist politics.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## What do these results mean for the upcoming election and Zohran Mamdani's political strategy?")
st.markdown("""
The key takeaway from these results is that racial diversity has a non-negligible effect on the likelihood that a voting population will favor socialist politics. What is extremely curious about these findings however is the ‘strangeness’ of populations within public housing districts, that tend to have high personal diversity scores and Shannon indices and were yet more likely to vote for Cuomo. Take for example this image of West-Queens below.
""")

if QUEENS_EXAMPLE_IMG.exists():
    st.image(
        str(QUEENS_EXAMPLE_IMG),
        caption="West-Queens Example: Diversity and Voting Patterns",
        use_container_width=True,
    )
else:
    st.error(f"Image not found: {QUEENS_EXAMPLE_IMG}. Make sure this file is in your repo at that path.")

st.markdown("""
In an area that tends to be very diverse, where almost every district voted overwhelmingly for Zohran Mamdani, the four areas that voted decidedly for Cuomo were areas with a majority of their population living within New York City public housing districts. 
This is a trend that has been mirrored across the city and has been additionally captured by the negative sign on the In Public Housing coefficient estimated by all five of the models above. What this means in terms of political strategy for Zohran Mamdani’s campaign, is that he should focus much of his effort within public housing districts for the remaining ten weeks before the election. Not only would this be an effective strategy given the sympathy of diverse electorates, but it would also have the potential to further galvanize the movement by speaking to voters that stand to gain the most from socialist policies. 
""")