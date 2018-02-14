<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="1.8.0-Lisboa" minimumScale="0" maximumScale="1e+08" hasScaleBasedVisibilityFlag="0">
  <transparencyLevelInt>255</transparencyLevelInt>
  <renderer-v2 symbollevels="0" type="RuleRenderer">
    <rules>
      <rule filter="&quot;tipo_us_s&quot;  = 'laterizio' and  &quot;stratigraph_index_us&quot; = 1" symbol="0" label="Caratterizzazione: Laterizio"/>
      <rule filter=" &quot;tipo_us_s&quot;  = 'sabbia concottata' and  &quot;stratigraph_index_us&quot; = 1" symbol="1" label="Caratterizzazione: Sabbia concottata"/>
      <rule filter="&quot;d_stratigrafica&quot; = 'Strato di carbone e cenere'  AND  &quot;stratigraph_index_us&quot;  = 2" symbol="2" label="Def. Stratigrafica: Strato di carbone e cenere"/>
      <rule filter="&quot;d_stratigrafica&quot; = 'Strato di sabbia concotta' AND  &quot;stratigraph_index_us&quot;  = 2&#xa;" symbol="3" label="Def. Stratigrafica: Strato di sabbia concotta"/>
      <rule filter=" &quot;d_stratigrafica&quot;  = 'Strato di terra' and  &quot;stratigraph_index_us&quot;  = 2" symbol="4" label="Def. Stratigrafica: Strato di terra"/>
      <rule filter=" &quot;d_stratigrafica&quot;  = 'Struttura in muratura' and  &quot;stratigraph_index_us&quot;  = 2" symbol="5" label="Def. Stratigrafica: Struttura in muratura"/>
      <rule filter=" &quot;d_stratigrafica&quot;  = 'Strato di argilla' and  &quot;stratigraph_index_us&quot;  = 2" symbol="6" label="Def. Stratigrafica: Strato di argilla"/>
      <rule filter="&quot;d_stratigrafica&quot; = 'Riempimento di argilla'  AND  &quot;stratigraph_index_us&quot;  = 2" symbol="7" label="Def. Stratigrafica: Riempimento di argilla"/>
      <rule filter=" &quot;d_stratigrafica&quot;  = 'Taglio' and  &quot;stratigraph_index_us&quot;  = 2" symbol="8" label="Def. Stratigrafica: Taglio"/>
      <rule filter=" &quot;tipo_us_s&quot;  = 'carbone' and  &quot;stratigraph_index_us&quot; = 1" symbol="9" label="Caratterizzazione: Carbone"/>
      <rule filter=" &quot;tipo_us_s&quot;  = 'ciottolo' and  &quot;stratigraph_index_us&quot; = 1" symbol="10" label="Caratterizzazione: Ciottolo"/>
      <rule filter=" &quot;tipo_us_s&quot;  = 'malta' and  &quot;stratigraph_index_us&quot; = 1" symbol="11" label="Caratterizzazione: Malta"/>
    </rules>
    <symbols>
      <symbol outputUnit="MM" alpha="1" type="fill" name="0">
        <layer pass="1" class="SimpleFill" locked="0">
          <prop k="color" v="195,107,36,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
        <layer pass="1" class="SimpleFill" locked="0">
          <prop k="color" v="252,176,70,255"/>
          <prop k="color_border" v="195,107,36,255"/>
          <prop k="offset" v="0.5,0.5"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
        <layer pass="1" class="SimpleFill" locked="0">
          <prop k="color" v="217,106,51,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="b_diagonal"/>
          <prop k="style_border" v="no"/>
          <prop k="width_border" v="0.26"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="1">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="222,207,93,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
        <layer pass="0" class="SVGFill" locked="0">
          <prop k="angle" v="0"/>
          <prop k="svgFile" v="/concotto.svg"/>
          <prop k="svgFillColor" v="#000000"/>
          <prop k="svgOutlineColor" v="#000000"/>
          <prop k="svgOutlineWidth" v="1"/>
          <prop k="width" v="20"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="10">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="121,121,121,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="-0.5,-0.5"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="226,226,226,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.08"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="11">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="204,199,181,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
        <layer pass="0" class="SVGFill" locked="0">
          <prop k="angle" v="0"/>
          <prop k="svgFile" v="/malta.svg"/>
          <prop k="svgFillColor" v="#000000"/>
          <prop k="svgOutlineColor" v="#000000"/>
          <prop k="svgOutlineWidth" v="1"/>
          <prop k="width" v="20"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="2">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="220,222,231,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
        <layer pass="0" class="SVGFill" locked="0">
          <prop k="angle" v="0"/>
          <prop k="svgFile" v="/carbone.svg"/>
          <prop k="svgFillColor" v="#000000"/>
          <prop k="svgOutlineColor" v="#000000"/>
          <prop k="svgOutlineWidth" v="1"/>
          <prop k="width" v="20"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="3">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="242,208,11,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
        <layer pass="0" class="SVGFill" locked="0">
          <prop k="angle" v="0"/>
          <prop k="svgFile" v="/concotto.svg"/>
          <prop k="svgFillColor" v="#000000"/>
          <prop k="svgOutlineColor" v="#000000"/>
          <prop k="svgOutlineWidth" v="1"/>
          <prop k="width" v="20"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="4">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="190,142,113,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="5">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="250,205,149,255"/>
          <prop k="color_border" v="233,181,122,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="no"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="6">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="168,148,94,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
        <layer pass="0" class="SVGFill" locked="0">
          <prop k="angle" v="0"/>
          <prop k="svgFile" v="/argilla.svg"/>
          <prop k="svgFillColor" v="#000000"/>
          <prop k="svgOutlineColor" v="#000000"/>
          <prop k="svgOutlineWidth" v="1"/>
          <prop k="width" v="20"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="7">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="168,148,94,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
        <layer pass="0" class="SVGFill" locked="0">
          <prop k="angle" v="0"/>
          <prop k="svgFile" v="/argilla.svg"/>
          <prop k="svgFillColor" v="#000000"/>
          <prop k="svgOutlineColor" v="#000000"/>
          <prop k="svgOutlineWidth" v="1"/>
          <prop k="width" v="20"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="8">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="255,255,255,255"/>
          <prop k="color_border" v="208,39,12,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="dash"/>
          <prop k="width_border" v="0.5"/>
        </layer>
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="166,170,150,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="no"/>
          <prop k="width_border" v="0.26"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="fill" name="9">
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="0,0,0,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="solid"/>
          <prop k="style_border" v="dot"/>
          <prop k="width_border" v="0.08"/>
        </layer>
        <layer pass="0" class="SimpleFill" locked="0">
          <prop k="color" v="167,152,147,255"/>
          <prop k="color_border" v="0,0,0,255"/>
          <prop k="offset" v="0,0"/>
          <prop k="style" v="horizontal"/>
          <prop k="style_border" v="solid"/>
          <prop k="width_border" v="0.26"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="line" name="@11@1">
        <layer pass="0" class="SimpleLine" locked="0">
          <prop k="capstyle" v="square"/>
          <prop k="color" v="0,0,0,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="0.26"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="line" name="@1@1">
        <layer pass="0" class="SimpleLine" locked="0">
          <prop k="capstyle" v="square"/>
          <prop k="color" v="0,0,0,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="0.26"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="line" name="@2@1">
        <layer pass="0" class="SimpleLine" locked="0">
          <prop k="capstyle" v="square"/>
          <prop k="color" v="0,0,0,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="0.26"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="line" name="@3@1">
        <layer pass="0" class="SimpleLine" locked="0">
          <prop k="capstyle" v="square"/>
          <prop k="color" v="0,0,0,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="0.26"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="line" name="@6@1">
        <layer pass="0" class="SimpleLine" locked="0">
          <prop k="capstyle" v="square"/>
          <prop k="color" v="0,0,0,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="0.26"/>
        </layer>
      </symbol>
      <symbol outputUnit="MM" alpha="1" type="line" name="@7@1">
        <layer pass="0" class="SimpleLine" locked="0">
          <prop k="capstyle" v="square"/>
          <prop k="color" v="0,0,0,255"/>
          <prop k="customdash" v="5;2"/>
          <prop k="joinstyle" v="bevel"/>
          <prop k="offset" v="0"/>
          <prop k="penstyle" v="solid"/>
          <prop k="use_custom_dash" v="0"/>
          <prop k="width" v="0.26"/>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
  <customproperties/>
  <displayfield>id_us</displayfield>
  <label>0</label>
  <labelattributes>
    <label fieldname="" text="Etichetta"/>
    <family fieldname="" name="MS Shell Dlg 2"/>
    <size fieldname="" units="pt" value="12"/>
    <bold fieldname="" on="0"/>
    <italic fieldname="" on="0"/>
    <underline fieldname="" on="0"/>
    <strikeout fieldname="" on="0"/>
    <color fieldname="" red="0" blue="0" green="0"/>
    <x fieldname=""/>
    <y fieldname=""/>
    <offset x="0" y="0" units="pt" yfieldname="" xfieldname=""/>
    <angle fieldname="" value="0" auto="0"/>
    <alignment fieldname="" value="center"/>
    <buffercolor fieldname="" red="255" blue="255" green="255"/>
    <buffersize fieldname="" units="pt" value="1"/>
    <bufferenabled fieldname="" on=""/>
    <multilineenabled fieldname="" on=""/>
    <selectedonly on=""/>
  </labelattributes>
  <edittypes>
    <edittype type="0" name="ROWID"/>
    <edittype type="0" name="ROWID_1"/>
    <edittype type="0" name="anno_scavo"/>
    <edittype type="0" name="area"/>
    <edittype type="0" name="area_s"/>
    <edittype type="0" name="attivita"/>
    <edittype type="0" name="campioni"/>
    <edittype type="0" name="colore"/>
    <edittype type="0" name="consistenza"/>
    <edittype type="0" name="cont_per"/>
    <edittype type="0" name="d_interpretativa"/>
    <edittype type="0" name="d_stratigrafica"/>
    <edittype type="0" name="data"/>
    <edittype type="0" name="data_schedatura"/>
    <edittype type="0" name="descrizione"/>
    <edittype type="0" name="disegnatore"/>
    <edittype type="0" name="documentazione"/>
    <edittype type="0" name="fase_finale"/>
    <edittype type="0" name="fase_iniziale"/>
    <edittype type="0" name="formazione"/>
    <edittype type="0" name="id"/>
    <edittype type="0" name="id_us"/>
    <edittype type="0" name="inclusi"/>
    <edittype type="0" name="interpretazione"/>
    <edittype type="0" name="metodo_di_scavo"/>
    <edittype type="0" name="order_layer"/>
    <edittype type="0" name="periodo_finale"/>
    <edittype type="0" name="periodo_iniziale"/>
    <edittype type="0" name="rapporti"/>
    <edittype type="0" name="rilievo_orginale"/>
    <edittype type="0" name="scavato"/>
    <edittype type="0" name="scavo_s"/>
    <edittype type="0" name="schedatore"/>
    <edittype type="0" name="sito"/>
    <edittype type="0" name="stato_di_conservazione"/>
    <edittype type="0" name="stratigraph_index_us"/>
    <edittype type="0" name="struttura"/>
    <edittype type="0" name="tipo_us_s"/>
    <edittype type="0" name="us"/>
    <edittype type="0" name="us_s"/>
  </edittypes>
  <editform>.</editform>
  <editforminit></editforminit>
  <annotationform>.</annotationform>
  <attributeactions/>
</qgis>
