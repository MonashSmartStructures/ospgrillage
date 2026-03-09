ospgui User Guide
=================

.. contents::
   :local:
   :depth: 2

Installation
============

``ospgui`` is a graphical interface for creating and visualizing bridge grillage models without writing Python code. It is built with **PyQt5** and distributed as an optional extension to **Ospgrillage**.

.. note::
   To use ``ospgui``, **Ospgrillage must be installed** first. Then, install the GUI with:

   .. code-block:: bash

      pip install ospgrillage[gui]

Launching the GUI
=================

After installation, launch the GUI from the command line:

.. code-block:: bash

   ospgui

Getting Started
===============

To get started with ``ospgui``:

1. Click **Apply Changes**, then **Create Geometry**.  
2. Once your geometry is created, you can adjust properties as needed.  
3. Use the GUI to generate the necessary files:
   - OpenSees command file  
   - Ospgrillage code  
   - Bridge deck mesh for analysis  

Features
========

`ospgui` streamlines bridge geometry creation with an intuitive interface. Key features include:

- **Interactive Geometry Setup**: Create straight, multi-span, skewed, or curved bridge geometries.  
- **Material and Section Assignment**: Choose from preset materials or define custom properties; assign cross-section details for all bridge members.  
- **Member Control**: Configure internal and edge beams, spacing, and offsets.  
- **Automatic Code Generation**: Generates Python scripts for Ospgrillage models and optionally OpenSees command files.  
- **Visualization**: Integrated visual feedback for the generated bridge mesh.  
- **Powerful Code View**: Users can review, edit, and execute **any Python script** directly in the GUI. You can also load external Python files from the File menu.

User Interface Overview
=======================

`ospgui` allows users to generate **OpenSeesPy scripts** for bridge mesh without manually writing Python scripts. The main window consists of:

- **Menu Bar**: **File** and **Create Geometry** options.  
- **Input Panels** (left): Tabs for geometry, materials, sections, and members.  
- **Code View** (right): Displays the generated Ospgrillage script, which can be edited and executed.

Menu Bar
--------

**File Menu**

- **New**: Start a new project  
- **Open**: Open an existing project  
- **Save**: Save current project  
- **Exit**: Close the application  

**Create Geometry Menu**

- **Create Geometry**: Executes the script shown in the **Code View**. The button 'Create Geometry' at the bottom left of ospgui has the same functionality as this.

Input Panels
------------

The left-side panel has four tabs:

- **Geometry**
- **Materials**
- **Sections**
- **Members**

Geometry Tab
------------

Define the bridge’s geometric and mesh properties.

.. figure:: _images/geometry_tab.png
   :alt: Geometry Tab in `ospgui`
   :align: center

**Basic Geometry**

- **Bridge Name**: Name of your model  
- **Length & Width**: Overall dimensions  
- **Left/Right Skew Angle**: Skew of bridge ends  

**Mesh Settings**

- **Bridge Type**: Straight, Multi-span, or Curved  
- **Longitudinal Beams**: Beams along the bridge length  
- **Transverse Beams**: Beams across the width  
- **Mesh Type**: Ortho or Oblique  

**Output Mode**

- **OpenSees Command File**: Export script for OpenSees  
- **Visualization**: Display the generated mesh  

Materials Tab
-------------

Define material properties for bridge components.

.. figure:: _images/materials_tab.png
   :alt: Materials Tab in `ospgui`
   :align: center

- **Material Type**: Concrete, Steel, etc.  
- **Preset Options**: Select standard codes and grades (e.g., AS5100-2017, 32MPa)  
- **Custom Values**: Manually input properties  

Sections Tab
------------

Define cross-sectional properties of bridge members.

.. figure:: _images/sections_tab.png
   :alt: Sections Tab in `ospgui`
   :align: center

- **Longitudinal Section**: Main beams  
- **Transverse Section**: Internal transverse beams  
- **End Transverse Section**: Beams at bridge ends  
- **Edge Longitudinal Section**: Edge beams  

Members Tab
-----------

Set member spacing and offsets.

.. figure:: _images/members_tab.png
   :alt: Members Tab in `ospgui`
   :align: center

- **External to Internal Distance**: Spacing between external and internal beams  
- **Edge Beams**: Offset from bridge edge  

Code View
---------

The **Code View** displays the generated **Ospgrillage script**, which can be:

- Reviewed and edited directly in the GUI  
- Executed using the **Create Geometry** button  
- Loaded with any external Python file via the File menu  

Generation and Visualization
----------------------------

- **Apply Changes**: Updates the code based on current input parameters  
- **Create Geometry**: Generates the bridge model  

Depending on the **Output Mode**, this either:

- Shows a visualization of the bridge mesh  
- Exports an OpenSees command file  

.. figure:: _images/visualization.png
   :alt: Visualization of Generated Bridge Mesh
   :align: center